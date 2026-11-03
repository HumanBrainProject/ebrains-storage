import os
from uuid import uuid4

import pytest

from ebrains_drive import DriveApiClient
from ebrains_drive.exceptions import DoesNotExist

# n.b. this test will do the following:
# if EBRAINS_INT_JWT envvar provided
#   will test drive-int.ebrains.eu default (My Library) repo
#   if EBRAINS_INT_REPO_ID envar provided:
#     will test drive-int.ebrains.eu repo_id=EBRAINS_INT_REPO_ID
# 
# if EBRAINS_PROD_JWT envvar provided
#   will test drive.ebrains.eu default (My Library) repo
#   if EBRAINS_PROD_REPO_ID envar provided:
#     will test drive.ebrains.eu repo_id=EBRAINS_INT_REPO_ID
#
# The JWT will _have_ to be personal (ie no client crednetial JWT), and must have collab.drive scope


EBRAINS_INT_JWT = os.getenv("EBRAINS_INT_JWT")
EBRAINS_PROD_JWT = os.getenv("EBRAINS_PROD_JWT")

EBRAINS_INT_REPO_ID = os.getenv("EBRAINS_INT_REPO_ID")
EBRAINS_PROD_REPO_ID = os.getenv("EBRAINS_PROD_REPO_ID")


def get_set_get_del(client: DriveApiClient, repo_id: str = None):

    fname = "ebrains-drive-test-" + str(uuid4()) + ".txt"
    content = "ebrains-drive-test content " + str(uuid4())
    repo = client.repos.get_default_repo() if repo_id is None else client.repos.get_repo(repo_id=repo_id)

    # first get, should raise
    with pytest.raises(DoesNotExist):
        repo.get_file("/" + fname)

    # set
    _dir = repo.get_dir("/")
    _dir.upload(content.encode(), fname)

    # get
    f = repo.get_file("/" + fname)
    assert f.get_content() == content.encode()

    # delete
    f.delete()

    # get should now raise
    with pytest.raises(DoesNotExist):
        repo.get_file("/" + fname)

    pass


@pytest.mark.parametrize(
    "token, env",
    [
        pytest.param(EBRAINS_INT_JWT, "int", id="int"),
        pytest.param(EBRAINS_PROD_JWT, "", id="prod"),
    ],
)
def test_default(token: str, env: str):
    if not token:
        pytest.skip(f"token not set, skipping")
        return
    client = DriveApiClient(token=token, env=env)
    get_set_get_del(client)


@pytest.mark.parametrize(
    "token, repo_id, env",
    [
        pytest.param(EBRAINS_INT_JWT, EBRAINS_INT_REPO_ID, "int", id="int"),
        pytest.param(EBRAINS_PROD_JWT, EBRAINS_PROD_REPO_ID, "", id="prod"),
    ],
)
def test_repo(token: str, repo_id: str, env: str):

    if not token:
        pytest.skip(f"token not set, skipping")
        return

    if not repo_id:
        pytest.skip(f"repo_id not set, skipping")
        return

    client = DriveApiClient(token=token, env=env)
    get_set_get_del(client, repo_id=repo_id)
