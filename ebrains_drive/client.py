import requests
from ebrains_drive.utils import urljoin
from ebrains_drive.exceptions import ClientHttpError
from ebrains_drive.repos import Repos
from ebrains_drive.file import File
import re

class DriveApiClient(object):
    """Wraps seafile web api"""
    def __init__(self, username=None, password=None, token=None, env=""):
        """Wraps various basic operations to interact with seahub http api.
        """
        self._set_env(env)

        self.server = self.drive_url
        
        self.username = username
        self.password = password
        self._token = token

        self.repos = Repos(self)
        self.groups = Groups(self)
        self.file = File(self)

        if token is None:
            self._get_token()

    def _set_env(self, env=''):
        self.suffix = ""

        if env == "dev":
            self.suffix = "-dev"
        elif env == "int":
            self.suffix = "-int"
        # else we keep empty suffix for production

        self.drive_url = "https://drive" + self.suffix + ".ebrains.eu"
        self.iam_host = "iam" + self.suffix + ".ebrains.eu"
        self.iam_url = "https://" + self.iam_host

    def get_drive_url(self):
        return self.drive_url
    
    def get_iam_host(self):
        return self.iam_host
    
    def get_iam_url(self):
        return self.iam_url

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

    def __str__(self):
        return 'DriveApiClient[server=%s, user=%s]' % (self.server, self.username)

    __repr__ = __str__

    def get(self, *args, **kwargs):
        return self._send_request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._send_request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._send_request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._send_request('delete', *args, **kwargs)

    def _send_request(self, method, url, *args, **kwargs):
        if not url.startswith('http'):
            url = urljoin(self.server, url)

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


class Groups(object):
    def __init__(self, client):
        pass

    def create_group(self, name):
        pass
