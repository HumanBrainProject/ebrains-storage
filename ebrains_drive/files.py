import io
import os
import posixpath
import re
import time
from typing import Any, Dict
import requests
from tqdm import tqdm
from ebrains_drive.utils import querystr, on_401_raise_unauthorized

# Note: only files and dirs with contents is assigned an ID; else their ID is set to all zeros
ZERO_OBJ_ID = "0000000000000000000000000000000000000000"


class _SeafDirentBase(object):
    """Base class for :class:`SeafFile` and :class:`SeafDir`.

    It provides implementation of their common operations.
    """

    isdir = None

    def __init__(self, repo, path, object_id, obj_type, size=0):
        """
        :param:`path` the full path of this entry within its repo, like
        "/documents/example.md"

        :param:`size` The size of a file. It should be zero for a dir.
        """
        self.client = repo.client
        self.repo = repo
        self.path = path
        self.id = object_id
        self.type = obj_type
        self.size = size

    @property
    def name(self):
        return posixpath.basename(self.path)

    def list_revisions(self):
        pass

    def delete(self):
        suffix = "dir" if self.isdir else "file"
        url = "/api2/repos/%s/%s/" % (self.repo.id, suffix) + querystr(p=self.path)
        resp = self.client.delete(url)
        return resp

    def rename(self, newname):
        """Change file/folder name to newname"""
        suffix = "dir" if self.isdir else "file"
        url = "/api2/repos/%s/%s/" % (self.repo.id, suffix) + querystr(p=self.path, reloaddir="true")
        postdata = {"operation": "rename", "newname": newname}
        resp = self.client.post(url, data=postdata)
        succeeded = resp.status_code == 200
        if succeeded:
            if self.isdir:
                new_dirent = self.repo.get_dir(os.path.join(os.path.dirname(self.path), newname))
            else:
                new_dirent = self.repo.get_file(os.path.join(os.path.dirname(self.path), newname))
            for key in list(self.__dict__.keys()):
                self.__dict__[key] = new_dirent.__dict__[key]
        return succeeded

    def _copy_move_task(self, operation, dirent_type, dst_dir, dst_repo_id=None):
        url = "/api/v2.1/copy-move-task/"
        src_repo_id = self.repo.id
        src_parent_dir = os.path.dirname(self.path)
        src_dirent_name = os.path.basename(self.path)
        dst_repo_id = dst_repo_id
        dst_parent_dir = dst_dir
        operation = operation
        dirent_type = dirent_type
        postdata = {
            "src_repo_id": src_repo_id,
            "src_parent_dir": src_parent_dir,
            "src_dirent_name": src_dirent_name,
            "dst_repo_id": dst_repo_id,
            "dst_parent_dir": dst_parent_dir,
            "operation": operation,
            "dirent_type": dirent_type,
        }
        return self.client.post(url, data=postdata)

    def copyTo(self, dst_dir, dst_repo_id=None):
        """Copy file/folder to other directory (also to a different repo)"""
        if dst_repo_id is None:
            dst_repo_id = self.repo.id

        dirent_type = "dir" if self.isdir else "file"
        resp = self._copy_move_task("copy", dirent_type, dst_dir, dst_repo_id)
        return resp.status_code == 200

    # snake_case alias for symmetry with the rest of the API
    copy_to = copyTo

    def moveTo(self, dst_dir, dst_repo_id=None):
        """Move file/folder to other directory (also to a different repo)"""
        if dst_repo_id is None:
            dst_repo_id = self.repo.id

        dirent_type = "dir" if self.isdir else "file"
        resp = self._copy_move_task("move", dirent_type, dst_dir, dst_repo_id)
        succeeded = resp.status_code == 200
        if succeeded:
            new_repo = self.client.repos.get_repo(dst_repo_id)
            dst_path = os.path.join(dst_dir, os.path.basename(self.path))
            if self.isdir:
                new_dirent = new_repo.get_dir(dst_path)
            else:
                new_dirent = new_repo.get_file(dst_path)
            for key in list(self.__dict__.keys()):
                self.__dict__[key] = new_dirent.__dict__[key]
        return succeeded

    move_to = moveTo

    def get_share_link(self):
        dirent_type = "dir" if self.isdir else "file"
        url = f"/api2/repos/{self.repo.id}/{dirent_type}/shared-link/"
        resp = self.client.put(url, data={"p": self.path}, expected=(200, 201))
        succeeded = resp.status_code in (200, 201)
        if succeeded:
            return resp.headers["Location"]
        else:
            return None


class SeafDir(_SeafDirentBase):
    isdir = True

    def __init__(self, *args, **kwargs):
        super(SeafDir, self).__init__(*args, **kwargs)
        self.entries = None
        self.entries = kwargs.pop("entries", None)

    def ls(self, entity_type=None, force_refresh=True):
        """List the entries in this dir.

        Return a list of objects of class :class:`SeafFile` or :class:`SeafDir`.
        """
        if entity_type and entity_type not in ["file", "dir"]:
            raise ValueError("Invalid value for parameter `entity_type`; must be 'file' or 'dir'!")
        if self.entries is None or force_refresh:
            self.load_entries()

        if entity_type:
            return [x for x in self.entries if x.type == entity_type]
        else:
            return self.entries

    def share_to_user(self, email, permission):
        url = "/api2/repos/%s/dir/shared_items/" % self.repo.id + querystr(p=self.path)
        putdata = {"share_type": "user", "username": email, "permission": permission}
        resp = self.client.put(url, data=putdata)
        return resp.status_code == 200

    def create_empty_file(self, name):
        """Create a new empty file in this dir.
        Return a :class:`SeafFile` object of the newly created file.
        """
        # TODO: file name validation
        path = posixpath.join(self.path, name)
        url = "/api2/repos/%s/file/" % self.repo.id + querystr(p=path, reloaddir="true")
        postdata = {"operation": "create"}
        resp = self.client.post(url, data=postdata)
        self.id = resp.headers["oid"]
        self.load_entries(resp.json())
        return SeafFile(self.repo, path, ZERO_OBJ_ID, "file", 0)

    def check_exists(self, name, entity_type=None):
        """Check if an entity with specified name exists in current directory
        Note: seafile doesn't allow even a sub-directory and file,
              within the same directory, to have the same name
        """
        entity_list = self.ls(entity_type=entity_type, force_refresh=True)
        for e in entity_list:
            if e.name == name:
                return e
        return False

    def mkdir(self, name):
        """Create a new sub folder right under this dir.

        Return a :class:`SeafDir` object of the newly created sub folder.
        """
        # check if entity with same name already exists
        if self.check_exists(name):
            raise FileExistsError("File/directory with name = `{}` already exists in current directory!".format(name))

        path = posixpath.join(self.path, name)
        url = "/api2/repos/%s/dir/" % self.repo.id + querystr(p=path, reloaddir="true")
        postdata = {"operation": "mkdir"}
        resp = self.client.post(url, data=postdata)
        self.id = resp.headers["oid"]
        self.load_entries(resp.json())

        # fetch and return created directory object
        return SeafDir(self.repo, path, ZERO_OBJ_ID, "dir")

    def download(self, name=None):
        """Download the entire contents of a directory as a zip file

        :param:name The name of the downloaded zip file.
            If None, the name of the directory (or repo name in case of root directory) would be used.

        Returns a dict in following format:
        {'zipped': NUM, 'total': NUM, 'failed': NUM, 'failed_reason': '', 'canceled': NUM}
        """
        download_token = self._get_download_token()
        url = "/api/v2.1/query-zip-progress/?token=%s" % (download_token)
        wait = True
        while wait:
            resp = self.client.get(url).json()
            if resp["total"] == resp["zipped"] + resp["failed"] + resp["canceled"]:
                wait = False
            else:
                time.sleep(1)
        if resp["total"] != resp["zipped"]:
            raise Exception(resp["failed_reason"])
        url = "%s/seafhttp/zip/%s" % (self.client.server, download_token)
        zip_data = self.client.get(url).content
        if name:
            name = name if name.endswith(".zip") else name + ".zip"
        else:
            name = "%s.zip" % (self.repo.name) if (self.path == "/") else "%s.zip" % (self.path.split("/")[-1])
        with open(name, "wb") as f:
            f.write(zip_data)
        return resp

    def _get_download_token(self):
        if self.path == "/":
            parent_dir = "/"
            dirents = [item.name for item in self.ls()]
        else:
            parent_dir = "/".join(self.path.split("/")[0:-1]) or "/"
            dirents = self.path.split("/")[-1]
        url = "/api/v2.1/repos/%s/zip-task/" % (self.repo.id)
        data = {
            "parent_dir": parent_dir,
            "dirents": dirents,
        }
        resp = self.client.post(url, data=data).json()
        return resp["zip_token"]

    def upload(self, fileobj, filename):
        """Upload a file to this folder.

        :param fileobj: file-like object, ``bytes``, or path (``str`` / ``PathLike``)
            to a local file. The path overload mirrors
            :meth:`ebrains_drive.bucket.Bucket.upload`.
        :param filename: The name of the file as stored in the folder.

        Return a :class:`SeafFile` object of the newly uploaded file.
        """
        if isinstance(fileobj, bytes):
            fileobj = io.BytesIO(fileobj)
        elif isinstance(fileobj, (str, os.PathLike)):
            with open(fileobj, "rb") as fp:
                return self.upload(fp, filename)
        upload_url = self._get_upload_link()
        files = {
            "file": (filename, fileobj),
            "parent_dir": self.path,
        }
        self.client.post(upload_url, files=files)
        return self.repo.get_file(posixpath.join(self.path, filename))

    def upload_local_file(self, filepath, name=None, overwrite=False):
        """Upload a file to this folder.

        :param:filepath The path to the local file
        :param:name The name of this new file. If None, the name of the local file would be used.

        Return a :class:`SeafFile` object of the newly uploaded file.
        """
        name = name or os.path.basename(filepath)

        # check if entity with same name already exists
        entity_obj = self.check_exists(name)
        if entity_obj:
            if overwrite:
                a = entity_obj.delete()
            else:
                raise FileExistsError(
                    "File/directory with name = `{}` already exists in current directory!".format(name)
                )

        with open(filepath, "rb") as fp:
            return self.upload(fp, name)

    def _get_upload_link(self):
        url = "/api2/repos/%s/upload-link/?p=%s" % (self.repo.id, self.path)
        resp = self.client.get(url)
        return re.match(r'"(.*)"', resp.text).group(1)

    def get_uploadable_sharelink(self):
        """Generate a uploadable shared link to this dir.

        Return the url of this link.
        """
        pass

    def load_entries(self, dirents_json=None):
        if dirents_json is None:
            url = "/api2/repos/%s/dir/" % self.repo.id + querystr(p=self.path)
            dirents_json = self.client.get(url).json()

        self.entries = [self._load_dirent(entry_json) for entry_json in dirents_json]

    def _load_dirent(self, dirent_json):
        path = posixpath.join(self.path, dirent_json["name"])
        if dirent_json["type"] == "file":
            return SeafFile(self.repo, path, dirent_json["id"], dirent_json["type"], dirent_json["size"])
        else:
            return SeafDir(self.repo, path, dirent_json["id"], dirent_json["type"], 0)

    @property
    def num_entries(self):
        if self.entries is None:
            self.load_entries()
        return len(self.entries) if self.entries is not None else 0

    def __str__(self):
        return "SeafDir[repo=%s, path=%s, entries=%s]" % (self.repo.id[:6], self.path, self.num_entries)

    __repr__ = __str__


class SeafFile(_SeafDirentBase):
    isdir = False

    def update(self, fileobj):
        """Update the content of this file"""
        pass

    def __str__(self):
        return "SeafFile[repo=%s, path=%s, size=%s]" % (self.repo.id[:6], self.path, self.size)

    __repr__ = __str__

    def get_download_link(self):
        return self._get_download_link()

    def _get_download_link(self):
        url = "/api2/repos/%s/file/" % self.repo.id + querystr(p=self.path)
        resp = self.client.get(url)
        return re.match(r'"(.*)"', resp.text).group(1)

    def get_content(self, *, progress=False):
        """Get the content of the file.

        :param progress: when ``True``, stream the response and display a
            ``tqdm`` progress bar. Mirrors
            :meth:`ebrains_drive.files.DataproxyFile.get_content`.
        """
        url = self._get_download_link()
        if not progress:
            return self.client.get(url).content

        resp = self.client.get(url, stream=True)
        total = resp.headers.get("content-length")
        content = bytearray()
        with tqdm(total=int(total) if total else None, leave=True) as bar:
            for chunk in resp.iter_content(4096):
                content.extend(chunk)
                bar.update(len(chunk))
        return bytes(content)


class DataproxyFile:
    session = requests.Session()

    def __init__(
        self, client, bucket, hash: str, last_modified: str, bytes: int, name: str, content_type: str, **kwargs
    ) -> None:
        # TODO kwargs may contain keys: storage, data

        self.client = client
        self.bucket = bucket

        self.hash = hash
        self.last_modified = last_modified
        self.bytes = bytes
        self.name = name
        self.content_type = content_type

    def __str__(self):
        return "DataproxyFile[bucket=%s, path=%s, size=%s]" % (self.bucket.name, self.name, self.bytes)

    __repr__ = __str__

    def get_download_link(self):
        """n.b. this download link expires in the order of seconds"""
        resp = self.client.get(
            f"/v1/{self.bucket.target}/{self.bucket.dataproxy_entity_name}/{self.name}", params={"redirect": False}
        )
        return resp.json().get("url")

    def get_content(self, *, progress=False):
        url = self.get_download_link()
        # Auth header must **NOT** be attached to the download link obtained, or we will get 401

        if not progress:
            return DataproxyFile.session.get(url).content

        content = bytearray()
        resp = DataproxyFile.session.get(url, stream=True)
        with tqdm(total=int(resp.headers.get("content-length")), leave=True) as progress:
            for c in resp.iter_content(4096):
                content.extend(c)
                progress.update(4096)
        return bytes(content)

    @classmethod
    def from_json(cls, client, bucket, file_json: Dict[str, Any]):
        return cls(client, bucket, **file_json)

    @on_401_raise_unauthorized("Unauthorized")
    def delete(self):
        resp = self.client.delete(f"/v1/{self.bucket.target}/{self.bucket.dataproxy_entity_name}/{self.name}")
        json_resp = resp.json()
        if "failures" in json_resp:
            assert len(json_resp.get("failures")) == 0
        else:
            assert "has been removed" in json_resp["detail"]

    @on_401_raise_unauthorized("Unauthorized")
    def copy_to(self, dst_name: str = None, *, dst_bucket: str = None):
        """Copy this object to another location.

        Uses the data-proxy's native copy endpoint (``PUT
        /v1/buckets/{name}/{object}/copy``). Roughly analogous to
        :meth:`ebrains_drive.files._SeafDirentBase.copy_to`.

        :param dst_name: destination object name; defaults to the same name
            (only meaningful when ``dst_bucket`` is set).
        :param dst_bucket: destination bucket name; defaults to the same
            bucket (only meaningful when ``dst_name`` is set).
        """
        if dst_name is None and dst_bucket is None:
            raise ValueError("copy_to requires at least one of dst_name or dst_bucket")
        params = {}
        if dst_bucket is not None:
            params["to"] = dst_bucket
        if dst_name is not None:
            params["name"] = dst_name
        resp = self.client.put(
            f"/v1/{self.bucket.target}/{self.bucket.dataproxy_entity_name}/{self.name}/copy",
            params=params,
        )
        return resp.status_code == 200


class BucketDir:
    """A virtual directory view over a flat data-proxy bucket.

    The data-proxy backend stores objects without any directory concept,
    but the DataProxy GUI presents objects with ``/`` in their names as
    a tree. ``BucketDir`` mirrors that convention so cross-backend code
    can traverse directories the same way for both
    :class:`ebrains_drive.repo.Repo` (via :class:`SeafDir`) and
    :class:`ebrains_drive.bucket.Bucket`.

    Instances are constructed via :meth:`ebrains_drive.bucket.Bucket.get_dir`
    or :meth:`get_dir` on another :class:`BucketDir`. No HTTP round-trip
    happens at construction time; child listings are fetched lazily.

    ``prefix`` is always stored without a leading slash. The root of the
    bucket is ``prefix=""``. A non-empty prefix never has a trailing
    slash internally — it is appended only when constructing API queries.
    """

    isdir = True

    def __init__(self, client, bucket, prefix: str = ""):
        self.client = client
        self.bucket = bucket
        self.prefix = prefix.strip("/")

    @property
    def name(self) -> str:
        """The last path segment of this directory, or ``""`` for the bucket root."""
        if not self.prefix:
            return ""
        return self.prefix.rsplit("/", 1)[-1]

    @property
    def path(self) -> str:
        """Absolute path of this directory within the bucket (always starts with ``/``)."""
        return "/" + self.prefix if self.prefix else "/"

    def _qualify(self, name: str) -> str:
        name = name.lstrip("/")
        if not self.prefix:
            return name
        return f"{self.prefix}/{name}"

    def _api_prefix(self) -> str:
        return f"{self.prefix}/" if self.prefix else ""

    def __str__(self):
        return "BucketDir[bucket=%s, path=%s]" % (self.bucket.name, self.path)

    __repr__ = __str__

    def ls(self, *, recursive: bool = False):
        """List the entries in this directory.

        :param recursive: when ``False`` (default), yield only the
            immediate children of this prefix — each is either a
            :class:`BucketDir` (a sub-prefix) or a :class:`DataproxyFile`
            (an object directly under this prefix). Uses the data-proxy
            ``delimiter`` parameter so the server returns grouped
            prefixes directly. When ``True``, yield every
            :class:`DataproxyFile` under this prefix at any depth.
        """
        if recursive:
            yield from self.bucket.ls(prefix=self._api_prefix() or None)
            return

        marker = None
        depth = self._api_prefix()
        LIMIT = 100
        while True:
            resp = self.client.get(
                f"/v1/{self.bucket.target}/{self.bucket.dataproxy_entity_name}",
                params={"limit": LIMIT, "marker": marker, "prefix": depth or None, "delimiter": "/"},
            )
            objects = resp.json().get("objects", [])
            if not objects:
                return
            for obj in objects:
                if "subdir" in obj:
                    child_prefix = obj["subdir"].rstrip("/")
                    marker = obj["subdir"]
                    yield BucketDir(self.client, self.bucket, child_prefix)
                else:
                    marker = obj.get("name")
                    yield DataproxyFile.from_json(self.client, self.bucket, obj)

    def get_file(self, name: str) -> "DataproxyFile":
        """Return the :class:`DataproxyFile` at ``<this prefix>/<name>``."""
        return self.bucket.get_file(self._qualify(name))

    def get_dir(self, name: str) -> "BucketDir":
        """Return a child :class:`BucketDir`. No HTTP request is made."""
        return BucketDir(self.client, self.bucket, self._qualify(name))

    def mkdir(self, name: str) -> "BucketDir":
        """Return a new :class:`BucketDir` for a child prefix.

        Object-storage directories exist purely by convention — they
        spring into existence when an object is uploaded under that
        prefix. This method performs no HTTP request and changes no
        server-side state.
        """
        return self.get_dir(name)

    def upload(self, filelike_or_path, filename: str, **kwargs):
        """Upload a file under this directory.

        Joins this directory's prefix with ``filename`` and delegates to
        :meth:`ebrains_drive.bucket.Bucket.upload`.
        """
        return self.bucket.upload(filelike_or_path, self._qualify(filename), **kwargs)

    def upload_local_file(self, filepath: str, name: str = None, overwrite: bool = False, **kwargs):
        """Upload a local file under this directory.

        Mirrors :meth:`SeafDir.upload_local_file`.
        """
        name = name or os.path.basename(filepath)
        return self.bucket.upload_local_file(filepath, self._qualify(name), overwrite=overwrite, **kwargs)

    def check_exists(self, name: str):
        """Return the matching :class:`DataproxyFile` / :class:`BucketDir`, or ``False``.

        Mirrors :meth:`SeafDir.check_exists`.
        """
        target = self._qualify(name).rstrip("/")
        for entry in self.ls():
            entry_name = entry.path.lstrip("/") if isinstance(entry, BucketDir) else entry.name
            if entry_name == target:
                return entry
        return False

    def delete(self, *, recursive: bool = False):
        """Delete every object under this prefix.

        Destructive: requires explicit ``recursive=True``. Raises
        :class:`ebrains_drive.exceptions.OperationError` otherwise.
        """
        if not recursive:
            from ebrains_drive.exceptions import OperationError

            raise OperationError(
                "BucketDir.delete() refuses to delete a directory implicitly. "
                "Pass recursive=True to delete every object under this prefix."
            )
        for obj in self.bucket.ls(prefix=self._api_prefix() or None):
            obj.delete()
