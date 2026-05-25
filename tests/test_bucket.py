import json
from contextlib import nullcontext
import pytest
from unittest.mock import patch, mock_open
from unittest.mock import MagicMock
from ebrains_drive.bucket import Bucket
from ebrains_drive.exceptions import ClientHttpError, Unauthorized, InvalidParameter, UpstreamAPIException
from io import StringIO, BytesIO, IOBase
from itertools import product
from tempfile import mkstemp
import os

# sentinel to make intent explicit and remove typo possibilities
TMP_PATH_SYMBOL = object()
STR_PATH_SYMBOL = object()
FILE_LIKE_SYMBOL = object()

class MockClient:
    def get(self, *args, **kwargs):
        raise NotImplementedError

    def put(self, *args, **kwargs):
        raise NotImplementedError


class MockHttpResp:
    def __init__(self, resp):
        self.resp = resp

    def json(self):
        return self.resp

    def raise_for_status(self): ...


bucket_json = {
    "name": "foo",
    "objects_count": 12,
    "bytes": 112233,
    "is_public": False,
    "role": "admin",
}

file_json1 = {
    "name": "foo",
    "hash": "hash-foo",
    "last_modified": "last-modified",
    "bytes": 123,
    "content_type": "json",
}


def test_from_json():
    client = MockClient()
    bucket = Bucket.from_json(client, bucket_json)
    assert isinstance(bucket, Bucket)


def test_ls_when_raise_client_error():

    client = MockClient()
    client.get = MagicMock()
    client.get.side_effect = [ClientHttpError(401, "foo-bar")]

    bucket = Bucket.from_json(client, bucket_json)

    try:
        fs = [f for f in bucket.ls()]
        raise Exception("did not raise")
    except Exception as e:
        assert isinstance(e, Unauthorized), f"Expect raise Unauthorized: {e}"


def test_ls_when_repeats():

    client = MockClient()
    client.get = MagicMock()
    client.get.side_effect = [MockHttpResp({"objects": [file_json1, file_json1]})]
    bucket = Bucket.from_json(client, bucket_json)

    try:
        fs = [f for f in bucket.ls()]
        raise Exception("did not raise")
    except Exception as e:
        assert isinstance(e, RuntimeError), f"Expect raise RuntimeError: {e}"


@pytest.fixture
def upload_fixture():

    mock_client = MockClient()
    mock_client.get = MagicMock()
    mock_client.put = MagicMock()

    mock_client.put.return_value = MockHttpResp({"url": "http://foo-bar.co/"})

    bucket = Bucket.from_json(mock_client, bucket_json)
    _, fname = mkstemp()

    with open(fname, "w") as fp:
        fp.write("foo-bar")

    try:

        with patch("requests.request") as mocked_request:
            mocked_request.return_value = MockHttpResp({})
            with patch("builtins.open", new_callable=mock_open) as patched_open:
                yield patched_open, mocked_request, bucket, fname
    finally:
        os.unlink(fname)


@pytest.mark.parametrize("filelike,kwargs", product([TMP_PATH_SYMBOL, StringIO()], [{"foo": "bar"}, {}]))
def test_upload(filelike, kwargs, upload_fixture):

    patched_open, mocked_request, bucket, tmp_filename = upload_fixture

    if filelike == TMP_PATH_SYMBOL:
        filelike = tmp_filename

    bucket.upload(filelike, "filename", **kwargs)
    if isinstance(filelike, str):
        patched_open.assert_called()
        data = patched_open.return_value
    elif isinstance(filelike, IOBase):
        patched_open.assert_not_called()
        data = filelike
    else:
        raise RuntimeError(f" should be either str or IOBase")
    mocked_request.assert_called_with("PUT", "http://foo-bar.co/", data=data, **kwargs)


# Patch to 64 bytes so tests don't need large files on disk.
SMALL_CHUNK_SIZE = 64


def _make_bucket():
    client = MockClient()
    return Bucket.from_json(client, bucket_json)


# --- _get_filesize ---

@pytest.mark.parametrize("make_input,expected_size,check_seek", [
    pytest.param(STR_PATH_SYMBOL, 11, False, id="str-path"),
    pytest.param(FILE_LIKE_SYMBOL, 42, True, id="file-like"),
])
def test_get_filesize(tmp_path, make_input, expected_size, check_seek):
    bucket = _make_bucket()
    if make_input is STR_PATH_SYMBOL:
        p = tmp_path / "sample.bin"
        p.write_bytes(b"hello world")
        input_ = str(p)
    else:
        input_ = BytesIO(b"x" * 42)
        input_.seek(5)  # advance pointer to confirm it gets reset
    assert bucket._get_filesize(input_) == expected_size
    if check_seek:
        assert input_.tell() == 0  # pointer restored to start


# --- _can_multipart_upload ---

def _write(path, data):
    path.write_bytes(data)
    return path

@pytest.mark.parametrize("make_input,expected_size,raises", [
    (lambda tmp_path: str(_write(tmp_path / "big.bin", b"0" * (SMALL_CHUNK_SIZE + 1))), SMALL_CHUNK_SIZE + 1, False),
    (lambda tmp_path: str(_write(tmp_path / "small.bin", b"tiny")),                     None,                 True),
    (lambda tmp_path: str(_write(tmp_path / "exact.bin", b"0" * SMALL_CHUNK_SIZE)),     None,                 True),
    (lambda tmp_path: BytesIO(b"0" * (SMALL_CHUNK_SIZE + 10)),                          SMALL_CHUNK_SIZE + 10, False),
])
@patch("ebrains_drive.bucket.EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE", SMALL_CHUNK_SIZE)
def test_can_multipart_upload(tmp_path, make_input, expected_size, raises):
    src = make_input(tmp_path)
    bucket = _make_bucket()
    if raises:
        with pytest.raises(InvalidParameter):
            bucket._can_multipart_upload(src)
    else:
        assert bucket._can_multipart_upload(src) == expected_size


# --- upload falls back to multipart_upload ---

SMALL_THRESHOLD = 128


@pytest.mark.parametrize("file_size,expect_multipart", [
    pytest.param(SMALL_THRESHOLD + 1, True,  id="exceeds-threshold"),
    pytest.param(SMALL_THRESHOLD,     False, id="at-threshold"),
])
@patch("ebrains_drive.bucket.EBRAINS_DRIVE_MULTIPART_THRESHOLD", SMALL_THRESHOLD)
def test_upload_multipart_threshold(tmp_path, file_size, expect_multipart):
    f = tmp_path / "file.bin"
    f.write_bytes(b"x" * file_size)

    mock_client = MockClient()
    mock_client.put = MagicMock(return_value=MockHttpResp({"url": "http://example.com/upload"}))
    bucket = Bucket.from_json(mock_client, bucket_json)

    with patch.object(bucket, "multipart_upload") as mock_multipart:
        with patch("requests.request", return_value=MockHttpResp({})):
            bucket.upload(str(f), "dest/file.bin", extra="kwarg")
        if expect_multipart:
            mock_multipart.assert_called_once_with(str(f), "dest/file.bin", extra="kwarg")
        else:
            mock_multipart.assert_not_called()


# --- multipart_upload ---

MULTIPART_CHUNK_SIZE = 64


def _make_multipart_bucket():
    client = MockClient()
    client.put = MagicMock()
    return Bucket.from_json(client, bucket_json), client


class MockPresignedResp:
    """Simulates a presigned-URL PUT response with an ETag header."""

    def __init__(self, etag="abc123"):
        self.headers = {"etag": f'"{etag}"'}

    def raise_for_status(self):
        pass


@pytest.mark.parametrize("use_file_path,data,expected_part_count", [
    (True,  b"A" * (MULTIPART_CHUNK_SIZE * 2 + 10), 3),
    (False, b"B" * (MULTIPART_CHUNK_SIZE + 5),       2),
])
@patch("ebrains_drive.bucket.EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE", MULTIPART_CHUNK_SIZE)
def test_multipart_upload_fresh(tmp_path, use_file_path, data, expected_part_count):
    """Full fresh upload from a file path or BytesIO: obtains uploadId, uploads parts, completes."""
    presigned_url = "http://presigned.example.com/part"

    if use_file_path:
        f = tmp_path / "big.bin"
        f.write_bytes(data)
        source = str(f)
        dest = "dest/big.bin"
    else:
        source = BytesIO(data)
        dest = "dest/stream.bin"

    bucket, client = _make_multipart_bucket()
    client.put.side_effect = (
        [MockHttpResp({"uploadId": "uid-fresh"})]
        + [MockHttpResp({"url": presigned_url})] * expected_part_count
        + [MockHttpResp({})]
    )

    with patch("requests.Session") as MockSession:
        sess = MockSession.return_value
        sess.put.return_value = MockPresignedResp("etag-x")
        bucket.multipart_upload(source, dest)

    assert sess.put.call_count == expected_part_count
    if use_file_path:
        assert not os.path.exists(source + ".multipart_manifest.json")


@patch("ebrains_drive.bucket.EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE", MULTIPART_CHUNK_SIZE)
def test_multipart_upload_resumes_from_manifest(tmp_path):
    """If a manifest exists, upload resumes from next_offset without re-uploading completed parts."""
    chunk = MULTIPART_CHUNK_SIZE
    data = b"C" * (chunk * 3)
    f = tmp_path / "resume.bin"
    f.write_bytes(data)

    upload_id = "uid-resume"
    existing_etags = {"1": "etag-part1"}
    manifest = {
        "upload_id": upload_id,
        "etag_maps": existing_etags,
        "next_offset": chunk,  # first chunk already uploaded
    }
    manifest_path = str(f) + ".multipart_manifest.json"
    with open(manifest_path, "w") as mf:
        json.dump(manifest, mf)

    bucket, client = _make_multipart_bucket()
    presigned_url = "http://presigned.example.com/part"

    client.put.side_effect = [
        MockHttpResp({"url": presigned_url}),   # part 2
        MockHttpResp({"url": presigned_url}),   # part 3
        MockHttpResp({}),                        # complete
    ]

    with patch("requests.Session") as MockSession:
        sess = MockSession.return_value
        sess.put.return_value = MockPresignedResp("etag-resumed")
        bucket.multipart_upload(str(f), "dest/resume.bin")

    # Only 2 parts uploaded (part 1 was already done)
    assert sess.put.call_count == 2
    # Manifest cleaned up after success
    assert not os.path.exists(manifest_path)


@pytest.mark.parametrize("put_side_effect,use_session", [
    (MockHttpResp({}), False),                                              # no uploadId
    ([MockHttpResp({"uploadId": "uid-nourl"}), MockHttpResp({})], True),   # no presigned URL
])
@patch("ebrains_drive.bucket.EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE", MULTIPART_CHUNK_SIZE)
def test_multipart_upload_raises_on_missing_server_field(tmp_path, put_side_effect, use_session):
    """UpstreamAPIException raised when the server omits uploadId or a presigned URL."""
    data = b"D" * (MULTIPART_CHUNK_SIZE + 1)
    f = tmp_path / "bad.bin"
    f.write_bytes(data)

    bucket, client = _make_multipart_bucket()
    if isinstance(put_side_effect, list):
        client.put.side_effect = put_side_effect
    else:
        client.put.return_value = put_side_effect

    ctx = patch("requests.Session") if use_session else nullcontext()
    with ctx:
        with pytest.raises(UpstreamAPIException):
            bucket.multipart_upload(str(f), "dest/bad.bin")
