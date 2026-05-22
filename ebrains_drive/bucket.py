from typing import Iterable
import json
import os
import requests
from ebrains_drive.exceptions import DoesNotExist, InvalidParameter, UpstreamAPIException
from ebrains_drive.files import DataproxyFile
from ebrains_drive.utils import on_401_raise_unauthorized
from io import IOBase
from tqdm import tqdm
from typing import Union

MULTIPART_CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB
MUST_USE_MULTIPART_THRESHOLD = 1024 * 1024 * 1024  # 1 GB


class Bucket(object):

    LIMIT = 100

    """
    A dataproxy bucket
    n.b. for a dataset bucket, role & is_public may be None
    """

    def __init__(
        self,
        client,
        name: str,
        objects_count: int,
        bytes: int,
        last_modified: str = None,
        is_public: bool = None,
        is_initialized: bool = None,
        role: str = None,
        *,
        public: bool = False,
        target: str = "buckets",
        dataset_id: str = None,
    ) -> None:
        if target != "buckets" and target != "datasets":
            raise InvalidParameter(
                f"Init Buckets exception: target can be left unset, but if set, must either be buckets or datasets"
            )
        if public:
            raise NotImplementedError(f"Access to public datasets/buckets NYI.")
        self.public = public
        self.target = target

        self.client = client

        self.name = name
        self.objects_count = objects_count
        self.bytes = bytes
        self.last_modified = last_modified
        self.is_public = is_public
        self.role = role
        self.is_initialized = is_initialized

        # n.b. for dataset bucket, dataset_id needs to be used for dataproxy_entity_name, but for collab bucket, name is used
        self.dataproxy_entity_name = dataset_id or name

    @classmethod
    def from_json(
        cls, client, bucket_json, *, public: bool = False, target: str = "buckets", dataset_id=None
    ) -> "Bucket":
        return cls(client, **bucket_json, public=public, target=target, dataset_id=dataset_id)

    def __str__(self):
        return "(name='{}')".format(self.name)

    def __repr__(self):
        return "ebrains_drive.bucket.Bucket(name='{}')".format(self.name)

    @on_401_raise_unauthorized("Unauthorized.")
    def ls(self, prefix: str = None) -> Iterable[DataproxyFile]:
        marker = None
        visited_name = set()
        while True:
            resp = self.client.get(
                f"/v1/{self.target}/{self.dataproxy_entity_name}",
                params={"limit": self.LIMIT, "marker": marker, "prefix": prefix},
            )
            objects = resp.json().get("objects", [])
            if len(objects) == 0:
                break

            for obj in objects:

                yield DataproxyFile.from_json(self.client, self, obj)
                marker = obj.get("name")

                if marker in visited_name:
                    raise RuntimeError(f"Bucket.ls error: hash {marker} has already been visited.")
                visited_name.add(marker)
        return

    @on_401_raise_unauthorized("Unauthorized")
    def get_file(self, name: str) -> DataproxyFile:
        name = name.lstrip("/")
        for file in self.ls(prefix=name):
            if file.name == name:
                return file
        raise DoesNotExist(f"Cannot find {name}.")

    def _get_filesize(self, filelike: Union[str, IOBase]) -> int:
        if isinstance(filelike, str):
            with open(filelike, "rb") as fp:
                return fp.seek(0, 2)
        pos = filelike.seek(0, 2)
        filelike.seek(0)
        return pos

    def _can_multipart_upload(self, filelike: Union[str, IOBase]) -> int:
        """Returns file size; raises InvalidParameter if not larger than MULTIPART_CHUNK_SIZE."""
        size = self._get_filesize(filelike)
        if size <= MULTIPART_CHUNK_SIZE:
            raise InvalidParameter(
                f"multipart_upload requires file size > {MULTIPART_CHUNK_SIZE} bytes ({size} bytes given). Use upload() instead."
            )
        return size

    @on_401_raise_unauthorized("Unauthorized")
    def multipart_upload(self, filelike: Union[str, IOBase], filename: str, **kwargs):
        """
        Upload a file using multipart upload to the ebrains drive, supporting resumable uploads.

        This method handles large file uploads by splitting them into chunks and uploading
        each chunk separately using presigned URLs. It supports resuming interrupted uploads
        via a local manifest file (`.multipart_manifest.json`), storing upload progress and
        ETags for completed parts.

        Parameters
        ----------
        filelike : str or IOBase
            Path to the local file as a string, or a file-like object (e.g., open file handle).
            If a string, the method opens and reads the file; if a file-like object, it must
            support `.seek()` and `.read()` operations.
        filename : str
            Destination filename in the remote storage. Leading slashes are stripped.
        **kwargs : dict, optional
            Additional keyword arguments (currently unused; included for extensibility).

        Notes
        -----
        - The manifest file is named `<filepath>.multipart_manifest.json` when a file path is provided.
        - The manifest stores:
            - `upload_id`: ID returned by the server for the multipart upload session.
            - `etag_maps`: Dictionary mapping part numbers to ETags of completed parts.
            - `next_offset`: Byte offset for the next chunk to upload (used for resuming).
        - In case of interruption, the method resumes from the last saved `next_offset`.
        - The manifest file is deleted upon successful completion of the upload.

        Raises
        ------
        UpstreamAPIException
            If the upload ID cannot be obtained from the server, or if a presigned URL
            is missing for a part, or if other required responses are malformed.
        """
        sess = requests.Session()
        filename = filename.lstrip("/")
        self._can_multipart_upload(filelike)

        filepath = filelike if isinstance(filelike, str) else None
        manifest_path = f"{filepath}.multipart_manifest.json" if filepath else None

        # Load manifest for resume, or start fresh
        manifest = {}
        if manifest_path and os.path.exists(manifest_path):
            with open(manifest_path) as f:
                manifest = json.load(f)

        upload_id = manifest.get("upload_id")
        etag_maps: dict = manifest.get("etag_maps", {})

        if not upload_id:
            resp = self.client.put(f"/v1/{self.target}/{self.dataproxy_entity_name}/{filename}/multipart")
            upload_id = resp.json().get("uploadId")
            if not upload_id:
                raise UpstreamAPIException("multipart_upload: failed to obtain uploadId.")
            manifest = {"upload_id": upload_id, "etag_maps": {}, "next_offset": 0}
            if manifest_path:
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f)

        next_offset = manifest.get("next_offset", 0)
        part_number = len(etag_maps) + 1
        file_size = self._get_filesize(filelike)

        filehandle = open(filepath, "rb") if filepath else filelike
        try:
            filehandle.seek(next_offset)
            with tqdm(
                total=file_size, initial=next_offset, unit="B", unit_scale=True, unit_divisor=1024, desc=filename
            ) as progress:
                while True:
                    chunk = filehandle.read(MULTIPART_CHUNK_SIZE)
                    if not chunk:
                        break
                    resp = self.client.put(
                        f"/v1/{self.target}/{self.dataproxy_entity_name}/{filename}/multipart/{upload_id}/{part_number}",
                        params={"redirect": "false"},
                    )
                    part_url = resp.json().get("url")
                    if not part_url:
                        raise UpstreamAPIException(f"multipart_upload: no presigned URL for part {part_number}.")
                    resp = sess.put(part_url, data=chunk)
                    resp.raise_for_status()
                    etag = resp.headers.get("etag", "").strip('"')
                    etag_maps[str(part_number)] = etag
                    next_offset += len(chunk)
                    progress.update(len(chunk))
                    if manifest_path:
                        manifest["etag_maps"] = etag_maps
                        manifest["next_offset"] = next_offset
                        with open(manifest_path, "w") as f:
                            json.dump(manifest, f)
                    part_number += 1
        finally:
            if filepath:
                filehandle.close()

        resp = self.client.put(
            f"/v1/{self.target}/{self.dataproxy_entity_name}/{filename}/multipart/{upload_id}",
            params={"redirect": "false"},
            json=etag_maps,
        )

        if manifest_path and os.path.exists(manifest_path):
            os.remove(manifest_path)

    @on_401_raise_unauthorized("Unauthorized")
    def upload(self, filelike: Union[str, IOBase], filename: str, **kwargs):
        """
        Upload a file to the bucket. If the file size exceeds `MUST_USE_MULTIPART_THRESHOLD` (1GB),
        this method automatically uses `multipart_upload` instead of a simple upload.

        Parameters
        ----------
        filelike : str or IOBase
            Path to the file or a file-like object (e.g., opened file handle).
        filename : str
            Destination filename in the bucket (leading slashes are stripped).
        **kwargs : dict, optional
            Additional keyword arguments passed to the underlying HTTP requests
            (e.g., headers, timeout, etc.).
        """
        if self._get_filesize(filelike) > MUST_USE_MULTIPART_THRESHOLD:
            # use multipart upload to stay way below 5G gateway limit
            return self.multipart_upload(filelike, filename, **kwargs)
        filename = filename.lstrip("/")
        resp = self.client.put(f"/v1/{self.target}/{self.dataproxy_entity_name}/{filename}", **kwargs)
        upload_url = resp.json().get("url")
        if upload_url is None:
            raise UpstreamAPIException(f"Bucket.upload did not get upload url.")
        filehandle = filelike if isinstance(filelike, IOBase) else open(filelike, "rb")
        resp = requests.request("PUT", upload_url, data=filehandle, **kwargs)
        resp.raise_for_status()
