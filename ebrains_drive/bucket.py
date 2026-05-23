import os
from typing import Iterable
import requests
from ebrains_drive.exceptions import DoesNotExist, InvalidParameter, UpstreamAPIException
from ebrains_drive.files import BucketDir, DataproxyFile
from ebrains_drive.utils import on_401_raise_unauthorized
from io import IOBase
from typing import Union


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
        objects_count: int = None,
        bytes: int = None,
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

    @on_401_raise_unauthorized("Unauthorized")
    def upload(self, filelike: Union[str, IOBase], filename: str, **kwargs):
        filename = filename.lstrip("/")
        resp = self.client.put(f"/v1/{self.target}/{self.dataproxy_entity_name}/{filename}", **kwargs)
        upload_url = resp.json().get("url")
        if upload_url is None:
            raise UpstreamAPIException(f"Bucket.upload did not get upload url.")
        filehandle = filelike if isinstance(filelike, IOBase) else open(filelike, "rb")
        resp = requests.request("PUT", upload_url, data=filehandle, **kwargs)
        resp.raise_for_status()

    def upload_local_file(self, filepath: str, name: str = None, overwrite: bool = False, **kwargs):
        """Upload a local file to this bucket.

        Mirrors :meth:`ebrains_drive.files.SeafDir.upload_local_file`.

        :param filepath: path to the local file on disk.
        :param name: name to store the file under in the bucket; defaults
            to the basename of ``filepath``.
        :param overwrite: when ``False`` (default), raise
            :class:`FileExistsError` if an object with that name already
            exists in the bucket. When ``True``, the existing object will
            be overwritten on upload.
        """
        name = name or os.path.basename(filepath)
        if not overwrite:
            try:
                self.get_file(name)
            except DoesNotExist:
                pass
            else:
                raise FileExistsError(f"Object with name = `{name}` already exists in bucket `{self.name}`.")
        with open(filepath, "rb") as fp:
            self.upload(fp, name, **kwargs)

    def delete(self):
        """Delete this bucket.

        Mirrors :meth:`ebrains_drive.repo.Repo.delete`. Delegates to
        :meth:`ebrains_drive.buckets.Buckets.delete_bucket` on the owning
        client so the call site is uniform across backends.
        """
        return self.client.buckets.delete_bucket(self.name)

    def is_readonly(self) -> bool:
        """Return ``True`` when the current credentials cannot write to this bucket.

        Conservative: dataset buckets and anonymously-accessed public
        buckets report read-only because their :attr:`role` is ``None``.
        Returns ``True`` when :attr:`role` is ``None`` or ``"viewer"``;
        otherwise ``False``.
        """
        return self.role in (None, "viewer")

    def get_dir(self, path: str) -> BucketDir:
        """Return a virtual directory view rooted at ``path``.

        The data-proxy backend is a flat object store; this method exposes
        the same prefix-based tree view the DataProxy GUI uses. Mirrors
        :meth:`ebrains_drive.repo.Repo.get_dir`. No HTTP round-trip on
        construction — listing happens lazily.
        """
        prefix = path.strip("/")
        return BucketDir(self.client, self, prefix)
