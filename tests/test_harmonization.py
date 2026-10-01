"""Tests for the harmonised Drive / Bucket surface.

These tests exercise the additions documented in
``docs`` and the README:

  * shared :mod:`ebrains_drive.base` Protocols
  * ``ebrains_drive.connect(target=...)`` entry point
  * :class:`Bucket.is_readonly` and the bug-fixed :class:`Repo.is_readonly`
  * :class:`BucketDir` virtual-directory view
  * Manager-level aliases (``get`` / ``list`` / ``create`` / ``delete``)
  * Bucket lifecycle aliases (``Buckets.create_bucket`` /
    ``Buckets.delete_bucket`` / ``Bucket.delete``) and the
    ``DeprecationWarning`` emitted by the legacy client methods.
"""

import pytest
import warnings
from io import BytesIO
from unittest.mock import MagicMock, patch

import ebrains_drive
from ebrains_drive.base import Container, ContainerManager, StorageObject
from ebrains_drive.bucket import Bucket
from ebrains_drive.buckets import Buckets
from ebrains_drive.client import BucketApiClient, DriveApiClient, _I_AM_A_PUBLIC_BUCKET
from ebrains_drive.exceptions import DoesNotExist, OperationError
from ebrains_drive.files import BucketDir, DataproxyFile
from ebrains_drive.repo import Repo


class MockResp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


class MockClient:
    suffix = ""

    def __init__(self):
        self.get = MagicMock()
        self.post = MagicMock()
        self.put = MagicMock()
        self.delete = MagicMock()
        self.send_request = MagicMock()


@pytest.fixture
def mock_client():
    return MockClient()


bucket_json = {
    "name": "foo",
    "objects_count": 12,
    "bytes": 112233,
    "is_public": False,
    "role": "editor",
}


# --------------------------- connect() ------------------------------ #


def test_connect_target_drive_default():
    with patch("ebrains_drive.DriveApiClient") as Drive, patch("ebrains_drive.BucketApiClient") as Bucket_:
        ebrains_drive.connect(token="dummy")
        Drive.assert_called_once_with(None, None, "dummy", "")
        Bucket_.assert_not_called()


def test_connect_target_bucket():
    with patch("ebrains_drive.DriveApiClient") as Drive, patch("ebrains_drive.BucketApiClient") as Bucket_:
        ebrains_drive.connect(token="dummy", target="bucket")
        Bucket_.assert_called_once_with(None, None, "dummy", "")
        Drive.assert_not_called()


def test_connect_target_unknown_raises():
    with pytest.raises(ValueError, match="Unknown target"):
        ebrains_drive.connect(token="dummy", target="banana")


# --------------------------- is_readonly() -------------------------- #


@pytest.mark.parametrize(
    "permission,expected",
    [("r", True), ("rw", False), ("rw", False)],
)
def test_repo_is_readonly(permission, expected):
    """Bug fix: previously raised AttributeError because of ``self.perm``."""
    repo = Repo(client=MockClient(), permission=permission)
    assert repo.is_readonly() is expected


@pytest.mark.parametrize(
    "role,expected",
    [(None, True), ("viewer", True), ("editor", False), ("administrator", False)],
)
def test_bucket_is_readonly(role, expected):
    bucket = Bucket(MockClient(), name="foo", objects_count=0, bytes=0, role=role)
    assert bucket.is_readonly() is expected


# --------------------------- Protocols ------------------------------ #


def test_repo_satisfies_container_protocol():
    repo = Repo(client=MockClient(), id="x", name="n", permission="rw")
    assert isinstance(repo, Container)


def test_bucket_satisfies_container_protocol(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    assert isinstance(bucket, Container)


def test_dataproxy_file_satisfies_storage_object_protocol(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    f = DataproxyFile(
        mock_client, bucket, hash="h", last_modified="now", bytes=1, name="x", content_type="text/plain"
    )
    assert isinstance(f, StorageObject)


def test_buckets_satisfies_container_manager_protocol(mock_client):
    assert isinstance(Buckets(mock_client), ContainerManager)


# --------------------------- Manager aliases ------------------------ #


def test_buckets_get_alias_delegates(mock_client):
    mock_client.get.return_value = MockResp(bucket_json)
    bkts = Buckets(mock_client)
    result = bkts.get("foo")
    assert isinstance(result, Bucket)
    mock_client.get.assert_called_with("/v1/buckets/foo/stat")


def test_buckets_list_calls_endpoint(mock_client):
    mock_client.get.return_value = MockResp(
        [
            {"name": "a", "role": "editor", "is_public": False},
            {"name": "b", "role": None, "is_public": True},
        ]
    )
    bkts = Buckets(mock_client)
    out = bkts.list_buckets()
    assert [b.name for b in out] == ["a", "b"]
    assert out[0].objects_count is None
    mock_client.get.assert_called_with("/v1/buckets", params=None)


def test_buckets_list_with_search(mock_client):
    mock_client.get.return_value = MockResp([])
    Buckets(mock_client).list_buckets(search="atlas")
    mock_client.get.assert_called_with("/v1/buckets", params={"search": "atlas"})


# --------------------------- Bucket.delete -------------------------- #


def test_bucket_delete_delegates_to_manager(mock_client):
    bkts = Buckets(mock_client)
    mock_client.buckets = bkts
    mock_client.send_request.return_value = MockResp({})
    bucket = Bucket.from_json(mock_client, bucket_json)
    bucket.delete()
    mock_client.send_request.assert_called_with("DELETE", "/v1/buckets/foo", expected=(200,))


# --------------------------- Deprecation ---------------------------- #


def test_create_new_emits_deprecation_warning():
    client = BucketApiClient.__new__(BucketApiClient)
    client._token = _I_AM_A_PUBLIC_BUCKET
    client.suffix = ""
    client.buckets = MagicMock()
    client.buckets.create_bucket.return_value = "ok"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.create_new("name")
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    client.buckets.create_bucket.assert_called_with("name", title=None, description="Created by ebrains_drive")


def test_delete_bucket_client_emits_deprecation_warning():
    client = BucketApiClient.__new__(BucketApiClient)
    client._token = _I_AM_A_PUBLIC_BUCKET
    client.suffix = ""
    client.buckets = MagicMock()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.delete_bucket("name", delete_wiki=True)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    client.buckets.delete_bucket.assert_called_with("name", delete_wiki=True)


# --------------------------- BucketDir ------------------------------ #


def test_bucket_get_dir_returns_root(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    root = bucket.get_dir("/")
    assert isinstance(root, BucketDir)
    assert root.prefix == ""
    assert root.path == "/"


def test_bucket_get_dir_nested(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    d = bucket.get_dir("/sub/folder/")
    assert d.prefix == "sub/folder"
    assert d.name == "folder"
    assert d.path == "/sub/folder"


def test_bucket_dir_ls_non_recursive_groups_subdirs(mock_client):
    """Non-recursive ``ls`` issues a request with delimiter="/" and dispatches
    mixed StorageObject / StorageDirWithObjectsResponse entries."""
    mock_client.get.side_effect = [
        MockResp(
            {
                "objects": [
                    {
                        "name": "a.txt",
                        "hash": "h",
                        "last_modified": "n",
                        "bytes": 1,
                        "content_type": "text/plain",
                    },
                    {"subdir": "dir1/", "bytes": None, "last_modified": None, "objects_count": None},
                    {"subdir": "dir2/", "bytes": None, "last_modified": None, "objects_count": None},
                ]
            }
        ),
        MockResp({"objects": []}),
    ]
    bucket = Bucket.from_json(mock_client, bucket_json)
    entries = list(bucket.get_dir("/").ls())
    types = [type(e).__name__ for e in entries]
    assert types == ["DataproxyFile", "BucketDir", "BucketDir"]
    assert entries[0].name == "a.txt"
    assert entries[1].prefix == "dir1"
    assert entries[2].prefix == "dir2"
    # Verify the delimiter param was actually sent
    call_params = mock_client.get.call_args_list[0].kwargs["params"]
    assert call_params["delimiter"] == "/"


def test_bucket_dir_ls_recursive_delegates_to_flat(mock_client):
    """Recursive ``ls`` delegates to ``Bucket.ls(prefix=...)`` (no delimiter)."""
    mock_client.get.return_value = MockResp({"objects": []})
    bucket = Bucket.from_json(mock_client, bucket_json)
    list(bucket.get_dir("/sub").ls(recursive=True))
    call_params = mock_client.get.call_args_list[0].kwargs["params"]
    assert "delimiter" not in call_params or call_params.get("delimiter") is None
    assert call_params["prefix"] == "sub/"


def test_bucket_dir_mkdir_is_local_only(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    new = bucket.get_dir("/").mkdir("future")
    assert isinstance(new, BucketDir)
    assert new.prefix == "future"
    mock_client.get.assert_not_called()
    mock_client.post.assert_not_called()
    mock_client.put.assert_not_called()


def test_bucket_dir_delete_requires_recursive(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    with pytest.raises(OperationError, match="recursive=True"):
        bucket.get_dir("/sub").delete()


def test_bucket_dir_delete_recursive_deletes_all(mock_client):
    f1 = MagicMock(spec=DataproxyFile)
    f2 = MagicMock(spec=DataproxyFile)
    bucket = Bucket.from_json(mock_client, bucket_json)
    with patch.object(bucket, "ls", return_value=iter([f1, f2])) as mock_ls:
        bucket.get_dir("/sub").delete(recursive=True)
    mock_ls.assert_called_with(prefix="sub/")
    f1.delete.assert_called_once()
    f2.delete.assert_called_once()


def test_bucket_dir_upload_qualifies_filename(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    with patch.object(bucket, "upload") as mock_upload:
        bucket.get_dir("/sub").upload(BytesIO(b"x"), "leaf.txt")
    args, _ = mock_upload.call_args
    assert args[1] == "sub/leaf.txt"


# --------------------------- copy_to -------------------------------- #


def test_dataproxy_file_copy_to_calls_native_endpoint(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    f = DataproxyFile(mock_client, bucket, hash="h", last_modified="n", bytes=1, name="src", content_type="t")
    mock_client.put.return_value = MockResp({}, status_code=200)
    ok = f.copy_to(dst_name="dst")
    assert ok is True
    mock_client.put.assert_called_with("/v1/buckets/foo/src/copy", params={"name": "dst"})


def test_dataproxy_file_copy_to_other_bucket(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    f = DataproxyFile(mock_client, bucket, hash="h", last_modified="n", bytes=1, name="src", content_type="t")
    mock_client.put.return_value = MockResp({}, status_code=200)
    f.copy_to(dst_bucket="otherbucket")
    mock_client.put.assert_called_with("/v1/buckets/foo/src/copy", params={"to": "otherbucket"})


def test_dataproxy_file_copy_to_requires_argument(mock_client):
    bucket = Bucket.from_json(mock_client, bucket_json)
    f = DataproxyFile(mock_client, bucket, hash="h", last_modified="n", bytes=1, name="src", content_type="t")
    with pytest.raises(ValueError):
        f.copy_to()


# --------------------------- BucketFile URL helper ------------------- #


def test_bucket_file_get_file_by_url_bucket():
    from ebrains_drive.file import BucketFile

    client = MagicMock()
    bucket = MagicMock()
    client.buckets.get_bucket.return_value = bucket
    helper = BucketFile(client)
    helper.get_file_by_url("https://data-proxy.ebrains.eu/api/v1/buckets/my-bucket/path/to/file.txt")
    client.buckets.get_bucket.assert_called_with("my-bucket")
    bucket.get_file.assert_called_with("path/to/file.txt")


def test_bucket_file_get_file_by_url_dataset():
    from ebrains_drive.file import BucketFile

    client = MagicMock()
    ds = MagicMock()
    client.buckets.get_dataset.return_value = ds
    helper = BucketFile(client)
    helper.get_file_by_url("https://data-proxy.ebrains.eu/api/v1/datasets/ds-uuid/a/b.csv")
    client.buckets.get_dataset.assert_called_with("ds-uuid")
    ds.get_file.assert_called_with("a/b.csv")


def test_bucket_file_get_file_by_url_invalid():
    from ebrains_drive.file import BucketFile

    helper = BucketFile(MagicMock())
    with pytest.raises(ValueError):
        helper.get_file_by_url("https://unrelated.example.com/foo")


# --------------------------- snake_case dirent aliases --------------- #


def test_seafdirent_snake_case_aliases_exist():
    from ebrains_drive.files import _SeafDirentBase

    assert _SeafDirentBase.move_to is _SeafDirentBase.moveTo
    assert _SeafDirentBase.copy_to is _SeafDirentBase.copyTo
