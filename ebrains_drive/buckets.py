from ebrains_drive.utils import on_401_raise_unauthorized
from ebrains_drive.bucket import Bucket

class Buckets(object):

    def __init__(self, client):
        self.client = client

    @on_401_raise_unauthorized('401 response. Check you/your token have access right and/or the bucket name has been spelt correctly.')
    def get_bucket(self, bucket_name: str) -> Bucket:
        """Get the specified bucket according name. If forced flag is set to True, will attempt to create the collab, if necessary.
        """
        resp = self.client.get(f"/v1/buckets/{bucket_name}/stat")
        return Bucket.from_json(self.client, resp.json())
