from ebrains_drive.exceptions import ClientHttpError, Unauthorized
from ebrains_drive.utils import on_401_raise_unauthorized
from ebrains_drive.bucket import Bucket
from time import sleep


class Buckets(object):

    def __init__(self, client):
        self.client = client

    @on_401_raise_unauthorized(
        "401 response. Check you/your token have access right and/or the bucket name has been spelt correctly."
    )
    def get_bucket(self, bucket_name: str, *, public: bool = False) -> Bucket:
        """Get the specified bucket according name. If forced flag is set to True, will attempt to create the collab, if necessary."""
        resp = self.client.get(f"/v1/buckets/{bucket_name}/stat")
        return Bucket.from_json(self.client, resp.json(), public=public, target="buckets")

    def get_dataset(self, dataset_id: str, *, public: bool = False, request_access: bool = False):
        request_sent = False
        attempt_no = 0
        while True:
            try:
                resp = self.client.get(f"/v1/datasets/{dataset_id}/stat")
                return Bucket.from_json(
                    self.client, resp.json(), public=public, target="datasets", dataset_id=dataset_id
                )
            except ClientHttpError as e:
                if e.code != 401:
                    raise e

                if not request_access:
                    raise Unauthorized(
                        f"You do not have access to this dataset. If this is a private dataset, try to set request_access flag to true. We can start the procedure of requesting access for you."
                    )
                if not request_sent:
                    self.client.post(f"/v1/datasets/{dataset_id}", expected=(200, 201))
                    request_sent = True
                    print("Request sent. Please check the mail box associated with the token.")
                sleep(5)
                attempt_no = attempt_no + 1
                print(f"Checking permission, attempt {attempt_no}")
