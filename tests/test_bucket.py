import pytest
from unittest.mock import patch, mock_open
from unittest.mock import MagicMock
from ebrains_drive.bucket import Bucket
from ebrains_drive.exceptions import ClientHttpError, Unauthorized
from io import StringIO, IOBase
from itertools import product
from tempfile import mkstemp
import os

TMP_PATH_SYMBOL = object()

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
