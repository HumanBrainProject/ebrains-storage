import json

import pytest
import requests

from ebrains_drive import BucketApiClient

@pytest.fixture
def bucket_client():
    yield BucketApiClient()

def test_get(bucket_client):
    url = "https://data-proxy.ebrains.eu/api/v1/buckets/reference-atlas-data/precomputed/BigBrainRelease.2015/8bit/info"
    bucket = bucket_client.buckets.get_bucket("reference-atlas-data")
    file = bucket.get_file("precomputed/BigBrainRelease.2015/8bit/info")
    file_json = json.loads(file.get_content())
    resp = requests.get(url)
    resp.raise_for_status()
    assert resp.json() == json.loads(file.get_content())
    assert file_json["type"] == "image"

