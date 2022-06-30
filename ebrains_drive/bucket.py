from typing import Iterable
import requests
from ebrains_drive.exceptions import DoesNotExist
from ebrains_drive.files import DataproxyFile
from ebrains_drive.utils import on_401_raise_unauthorized

class Bucket(object):

    LIMIT = 10

    """
    A dataproxy bucket
    """
    def __init__(self, client, name: str, objects_count: int, bytes: int, last_modified: str, is_public: bool, role: str) -> None:
        self.client = client
        # Would have been a lot easier to use dataclass, but keep dependency to a minimum
        self.name = name
        self.objects_count = objects_count
        self.bytes = bytes
        self.last_modified = last_modified
        self.is_public = is_public
        self.role = role

    @classmethod
    def from_json(cls, client, bucket_json) -> 'Bucket':
        return cls(client, **bucket_json)

    def __str__(self):
        return "(name='{}')".format(self.name)

    def __repr__(self):
        return "ebrains_drive.bucket.Bucket(name='{}')".format(self.name)

    @on_401_raise_unauthorized("Unauthorized.")
    def ls(self, prefix: str=None) -> Iterable[DataproxyFile]:
        marker = None
        visited_name = set()
        while True:
            resp = self.client.get(f"/v1/buckets/{self.name}", params={
                'limit': self.LIMIT,
                'marker': marker,
                'prefix': prefix
            })
            objects = resp.json().get("objects", [])
            if len(objects) == 0:
                break

            for obj in objects:

                yield DataproxyFile.from_json(self.client, self, obj)
                marker = obj.get("name")

                if marker in visited_name:
                    raise RuntimeError(f"Bucket.ls error: hash {marker} has already been visited.")
                visited_name.add(marker)
        return

    @on_401_raise_unauthorized("Unauthorized")
    def get_file(self, name: str) -> DataproxyFile:
        name = name.lstrip("/")
        for file in self.ls(prefix=name):
            if file.name == name:
                return file
        raise DoesNotExist(f"Cannot find {name}.")
    
    @on_401_raise_unauthorized("Unauthorized")
    def upload(self, fileobj: str, filename: str):
        filename = filename.lstrip("/")
        resp = self.client.put(f"/v1/buckets/{self.name}/{filename}")
        upload_url = resp.json().get("url")
        if upload_url is None:
            raise RuntimeError(f"Bucket.upload did not get upload url.")
        resp = requests.request("PUT", upload_url, data=open(fileobj, 'rb'))
        resp.raise_for_status()
