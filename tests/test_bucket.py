import pytest
from unittest.mock import MagicMock
from ebrains_drive.bucket import Bucket
from ebrains_drive.exceptions import ClientHttpError, Unauthorized

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

bucket_json={
    'name': 'foo',
    'objects_count': 12,
    'bytes': 112233,
    'last_modified': 'foo-bar',
    'is_public': False,
    'role': 'admin',
}

file_json1={
    'name': 'foo',
    'hash': 'hash-foo',
    'last_modified': 'last-modified',
    'bytes': 123,
    'content_type': 'json'
}



def test_from_json():
    client = MockClient()
    bucket = Bucket.from_json(client, bucket_json)
    assert isinstance(bucket, Bucket)

def test_ls_when_raise_client_error():

    client = MockClient()
    client.get = MagicMock()
    client.get.side_effect = [
        ClientHttpError(401, "foo-bar")
    ]
    
    bucket = Bucket.from_json(client, bucket_json)

    try:
        fs = [f for f in bucket.ls()]
        raise Exception("did not raise")
    except Exception as e:
        assert isinstance(e, Unauthorized), f"Expect raise Unauthorized: {e}"

def test_ls_when_repeats():

    client = MockClient()
    client.get = MagicMock()
    client.get.side_effect = [
        MockHttpResp({
            'objects': [file_json1, file_json1]
        })
    ]
    bucket = Bucket.from_json(client, bucket_json)

    try:
        fs = [f for f in bucket.ls()]
        raise Exception("did not raise")
    except Exception as e:
        assert isinstance(e, RuntimeError), f"Expect raise RuntimeError: {e}"
