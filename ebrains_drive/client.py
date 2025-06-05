from getpass import getpass
import requests
from abc import ABC
import base64
import json
import time
from copy import copy, deepcopy
from ebrains_drive.utils import on_401_raise_unauthorized
from ebrains_drive.exceptions import ClientHttpError, TokenExpired, Unauthorized
from ebrains_drive.repos import Repos
from ebrains_drive.buckets import Buckets
from ebrains_drive.file import File


class ClientBase(ABC):
    def __init__(self, username=None, password=None, token=None, env="") -> None:

        self.username = username
        self.password = password
        self._token = token
        self.server = None
        self.session = requests.Session()

        if token is None:
            if self.username is None:
                self.username = input("EBRAINS username: ")
            if self.password is None:
                self.password = getpass()

            try:
                self._get_token()
            except KeyError:
                print("Error: Invalid user credentials!")
                raise

    def _set_env(self, env=""):
        self.suffix = ""

        if env == "dev":
            self.suffix = "-dev"
        elif env == "int":
            self.suffix = "-int"
        # else we keep empty suffix for production

        self.iam_host = "iam" + self.suffix + ".ebrains.eu"
        self.iam_url = "https://" + self.iam_host

    def _get_token(self):
        response = requests.post(
            self.iam_url + "/auth/realms/hbp/protocol/openid-connect/token",
            auth=("ebrains-drive", ""),
            data={"grant_type": "password", "username": self.username, "password": self.password, "scope": "openid"},
        )

        if response.status_code == 200:
            self._token = response.json()["access_token"]
        elif response.status_code == 401:
            raise Unauthorized(response.json()["error_description"])
        else:
            raise ClientHttpError(response.json()["error_description"])

    def get(self, *args, **kwargs):
        return self.send_request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.send_request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.send_request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.send_request("DELETE", *args, **kwargs)

    def send_request(self, method: str, url: str, *args, **kwargs):
        if not url.startswith("http"):
            # sanity checks.
            # - accounts for if server was provided with trailing slashes
            # - accounts for if url was provided with leading slashes
            url = self.server.rstrip("/") + "/" + url.lstrip("/")

        # Copy the kwargs, and deepcopy the ones we change, so as not to mutate the original kwargs.
        # We cannot deepcopy the whole thing, because some values (e.g. BufferedReader objects)
        # cannot be pickled
        kwargs = copy(kwargs)
        headers = deepcopy(kwargs.get("headers", {}))
        headers.setdefault("Authorization", "Bearer " + self._token)
        kwargs["headers"] = headers

        expected = kwargs.pop("expected", 200)
        if not hasattr(expected, "__iter__"):
            expected = (expected,)
        resp = self.session.request(method, url, *args, **kwargs)
        if resp.status_code not in expected:
            msg = "Expected %s, but get %s" % (" or ".join(map(str, expected)), resp.status_code)
            raise ClientHttpError(resp.status_code, msg)

        return resp


class DriveApiClient(ClientBase):
    """Wraps seafile web api"""

    def __init__(self, username=None, password=None, token=None, env=""):
        """Wraps various basic operations to interact with seahub http api."""
        self._set_env(env)
        super().__init__(username, password, token, env)

        self.server = self.drive_url

        self.repos = Repos(self)
        self.groups = Groups(self)
        self.file = File(self)

    def _set_env(self, env=""):
        super()._set_env(env)
        self.drive_url = "https://drive" + self.suffix + ".ebrains.eu"

    def get_drive_url(self):
        return self.drive_url

    def get_iam_host(self):
        return self.iam_host

    def get_iam_url(self):
        return self.iam_url

    def __str__(self):
        return "DriveApiClient[server=%s, user=%s]" % (self.server, self.username)

    __repr__ = __str__

    def send_request(self, method: str, url: str, *args, **kwargs):
        if not url.startswith("http"):
            assert not self.server.endswith("/")
            if url.startswith("/"):
                url = f"{self.server}{url}"
            else:
                url = f"{self.server}/{url}"
        return super().send_request(method, url, *args, **kwargs)


_I_AM_A_PUBLIC_BUCKET = "_I_AM_A_PUBLIC_BUCKET"


class BucketApiClient(ClientBase):

    def __init__(self, username=None, password=None, token=_I_AM_A_PUBLIC_BUCKET, env="") -> None:
        self._set_env(env)

        super().__init__(username, password, token, env)

        self.server = f"https://data-proxy{self.suffix}.ebrains.eu/api"

        self.buckets = Buckets(self)

    @on_401_raise_unauthorized(
        "Failed. Note: BucketApiClient.create_new needs to have clb.drive:write as a part of scope."
    )
    def create_new(self, bucket_name: str, title=None, description="Created by ebrains_drive"):
        """
        Create a new bucket by first attempting to create a new wiki/collab. On 201 (created)
        or 409 (conflict) initialize the bucket of the said wiki. The request to initialize the bucket
        will be retried up to 5 times, as it usually takes a few minutes for the newly initialized wiki
        to allow buckets to be created.

        :param:`bucket_name` the name of the to-be-created bucket (and wiki if needed)

        :param:`title` the title of the to-be-created wiki (if unset, defaults to `bucket_name` param)

        :param:`description` description of the to-be-created wiki.
        """

        self.send_request(
            "POST",
            f"https://wiki{self.suffix}.ebrains.eu/rest/v1/collabs",
            json={
                "name": bucket_name,
                "title": title or bucket_name,
                "description": description,
                "drive": True,
                "chat": True,
                "public": False,
            },
            expected=(201, 409),
        )

        fuse = 5
        while True:
            try:
                self.send_request("POST", "/v1/buckets", json={"bucket_name": bucket_name}, expected=201)
                break
            except Exception as e:
                if fuse < 0:
                    raise e from e
                fuse -= 1
                time.sleep(1)

    @on_401_raise_unauthorized(
        "Failed. Note: BucketApiClient.delete_bucket needs to have clb.drive:write as a part of scope."
    )
    def delete_bucket(self, bucket_name: str, *, delete_wiki=False):
        """
        Deletes an existing bucket.

        :param:`bucket_name` name of the bucket (and - if delete_wiki is set - of the wiki) to be deleted

        :param:`delete_wiki` if the wiki should also be deleted.
        """
        self.send_request("DELETE", f"/v1/buckets/{bucket_name}", expected=(200,))
        if delete_wiki:
            self.send_request("DELETE", f"https://wiki.ebrains.eu/rest/v1/collabs/{bucket_name}", expected=(200,))

    def send_request(self, method: str, url: str, *args, **kwargs):

        if self._token != _I_AM_A_PUBLIC_BUCKET:
            hdr, info, sig = self._token.split(".")
            info_json = base64.b64decode(info + "==").decode("utf-8")

            # https://www.rfc-editor.org/rfc/rfc7519#section-2
            exp_utc_seconds = json.loads(info_json).get("exp")
            now_tc_seconds = time.time()

            if now_tc_seconds > exp_utc_seconds:
                raise TokenExpired

        if self._token == _I_AM_A_PUBLIC_BUCKET:
            headers = kwargs.get("headers", {})
            headers["Authorization"] = None
            kwargs["headers"] = headers

        return super().send_request(method, url, *args, **kwargs)


class Groups(object):
    def __init__(self, client):
        pass

    def create_group(self, name):
        pass
