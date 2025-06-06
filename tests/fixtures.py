# coding: utf-8

import os
import pytest

import ebrains_drive
from tests.utils import randstring


USER = os.environ.get("SEAFILE_TEST_USERNAME", "test@seafiletest.com")
PASSWORD = os.environ.get("SEAFILE_TEST_PWD", None)
TOKEN = os.environ.get("SEAFILE_TEST_TOKEN", None)


@pytest.fixture(scope="session")
def client():
    if TOKEN:
        return ebrains_drive.client.DriveApiClient(username=USER, token=TOKEN, env="int")
    elif PASSWORD:
        return ebrains_drive.client.DriveApiClient(username=USER, password=PASSWORD, env="int")
    else:
        pytest.skip(
            "Must define one of the following environment variables: " "SEAFILE_TEST_PWD or SEAFILE_TEST_TOKEN"
        )


@pytest.fixture(scope="function")
def repo(client):
    repo_name = "tmp-测试资料库-%s" % randstring()
    repo = client.repos.create_repo(repo_name)
    try:
        yield repo
    finally:
        repo.delete()
