from getpass import getpass
import requests
from abc import ABC
import base64
import json
import time
from ebrains_drive.utils import urljoin, on_401_raise_unauthorized
from ebrains_drive.exceptions import ClientHttpError, TokenExpired
from ebrains_drive.repos import Repos
from ebrains_drive.buckets import Buckets
from ebrains_drive.file import File

class ClientBase(ABC):
    def __init__(self, username=None, password=None, token=None, env="") -> None:

        self.username = username
        self.password = password
        self._token = token
        self.server = None

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


    def _set_env(self, env=''):
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
            self.iam_url+'/auth/realms/hbp/protocol/openid-connect/token',
            auth=('ebrains-drive', ''),
            data={
                'grant_type':'password',
                'username':self.username,
                'password':self.password
            })
        self._token = response.json()['access_token']
    
    def get(self, *args, **kwargs):
        return self.send_request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.send_request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.send_request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.send_request('DELETE', *args, **kwargs)

    def send_request(self, method: str, url: str, *args, **kwargs):
        if not url.startswith('http'):
            # sanity checks.
            # - accounts for if server was provided with trailing slashes
            # - accounts for if url was provided with leading slashes
            url = self.server.rstrip('/') + '/' + url.lstrip('/')

        headers = kwargs.get('headers', {})
        headers.setdefault('Authorization', 'Bearer ' + self._token)
        kwargs['headers'] = headers

        expected = kwargs.pop('expected', 200)
        if not hasattr(expected, '__iter__'):
            expected = (expected, )
        resp = requests.request(method, url, *args, **kwargs)
        if resp.status_code not in expected:
            msg = 'Expected %s, but get %s' % \
                  (' or '.join(map(str, expected)), resp.status_code)
            raise ClientHttpError(resp.status_code, msg)

        return resp

class DriveApiClient(ClientBase):
    """Wraps seafile web api"""
    def __init__(self, username=None, password=None, token=None, env=""):
        """Wraps various basic operations to interact with seahub http api.
        """
        self._set_env(env)
        super().__init__(username, password, token, env)

        self.server = self.drive_url

        self.repos = Repos(self)
        self.groups = Groups(self)
        self.file = File(self)

    def _set_env(self, env=''):
        super()._set_env(env)
        self.drive_url = "https://drive" + self.suffix + ".ebrains.eu"

    def get_drive_url(self):
        return self.drive_url

    def get_iam_host(self):
        return self.iam_host

    def get_iam_url(self):
        return self.iam_url

    def __str__(self):
        return 'DriveApiClient[server=%s, user=%s]' % (self.server, self.username)

    __repr__ = __str__

    def send_request(self, method: str, url: str, *args, **kwargs):
        if not url.startswith('http'):
            url = urljoin(self.server, url)
        return super().send_request(method, url, *args, **kwargs)

class BucketApiClient(ClientBase):

    def __init__(self, username=None, password=None, token=None, env="") -> None:
        if env != "":
            raise NotImplementedError("non prod environment for dataproxy access has not yet been implemented.")
        self._set_env(env)
        
        super().__init__(username, password, token, env)

        self.server = "https://data-proxy.ebrains.eu/api"

        self.buckets = Buckets(self)

    @on_401_raise_unauthorized("Failed. Note: BucketApiClient.create_new needs to have clb.drive:write as a part of scope.")
    def create_new(self, bucket_name: str, title=None, description="Created by ebrains_drive"):
        # attempt to create new collab
        self.send_request("POST", "https://wiki.ebrains.eu/rest/v1/collabs", json={
            "name": bucket_name,
            "title": title or bucket_name,
            "description": description,
            "drive": True,
            "chat": True,
            "public": False
        }, expected=201)

        # activate the bucket for the said collab
        self.send_request("POST", "/v1/buckets", json={
            "bucket_name": bucket_name
        }, expected=201)
    
    @on_401_raise_unauthorized("Failed. Note: BucketApiClient.create_new needs to have clb.drive:write as a part of scope.")
    def delete_bucket(self, bucket_name: str):
        self.send_request("DELETE", f"/v1/buckets/{bucket_name}")
    
    def send_request(self, method: str, url: str, *args, **kwargs):
        hdr, info, sig = self._token.split('.')
        info_json = base64.b64decode(info + '==').decode('utf-8')

        # https://www.rfc-editor.org/rfc/rfc7519#section-2
        exp_utc_seconds = json.loads(info_json).get('exp')
        now_tc_seconds = time.time()

        if now_tc_seconds > exp_utc_seconds:
            raise TokenExpired
        
        return super().send_request(method, url, *args, **kwargs)


class Groups(object):
    def __init__(self, client):
        pass

    def create_group(self, name):
        pass
