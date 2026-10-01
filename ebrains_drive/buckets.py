import time
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

    # ----- Harmonised aliases (mirror Repos.get/list/create/delete) -----

    def get(self, name: str, *, public: bool = False) -> Bucket:
        """Alias for :meth:`get_bucket`. Part of the harmonised
        :class:`ebrains_drive.base.ContainerManager` surface."""
        return self.get_bucket(name, public=public)

    @on_401_raise_unauthorized(
        "Failed. Note: Buckets.create_bucket needs to have clb.drive:write as a part of scope."
    )
    def create_bucket(self, bucket_name: str, title: str = None, description: str = "Created by ebrains_drive"):
        """Create a new bucket.

        Canonical entry point — :meth:`ebrains_drive.client.BucketApiClient.create_new`
        is a deprecated wrapper around this method.

        Creates a new wiki/collab first (or accepts an existing one),
        then initialises the bucket. Bucket initialisation is retried up
        to five times because the wiki backend usually needs a few
        seconds before it will accept bucket creation.

        :param bucket_name: name of the bucket (and wiki, if it needs creating).
        :param title: title of the wiki to create; defaults to ``bucket_name``.
        :param description: description for the wiki to create.
        """
        self.client.send_request(
            "POST",
            f"https://wiki{self.client.suffix}.ebrains.eu/rest/v1/collabs",
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
                self.client.send_request("POST", "/v1/buckets", json={"bucket_name": bucket_name}, expected=201)
                break
            except Exception as e:
                if fuse < 0:
                    raise e from e
                fuse -= 1
                time.sleep(1)
        return self.get_bucket(bucket_name)

    def create(self, name: str, **kwargs):
        """Alias for :meth:`create_bucket`."""
        return self.create_bucket(name, **kwargs)

    @on_401_raise_unauthorized(
        "Failed. Note: Buckets.delete_bucket needs to have clb.drive:write as a part of scope."
    )
    def delete_bucket(self, bucket_name: str, *, delete_wiki: bool = False):
        """Delete an existing bucket.

        Canonical entry point — :meth:`ebrains_drive.client.BucketApiClient.delete_bucket`
        is a deprecated wrapper around this method, and
        :meth:`ebrains_drive.bucket.Bucket.delete` delegates here.

        :param bucket_name: name of the bucket to delete.
        :param delete_wiki: when ``True``, also delete the associated wiki/collab.
        """
        self.client.send_request("DELETE", f"/v1/buckets/{bucket_name}", expected=(200,))
        if delete_wiki:
            self.client.send_request(
                "DELETE", f"https://wiki.ebrains.eu/rest/v1/collabs/{bucket_name}", expected=(200,)
            )

    def delete(self, name: str, **kwargs):
        """Alias for :meth:`delete_bucket`."""
        return self.delete_bucket(name, **kwargs)

    @on_401_raise_unauthorized("Unauthorized. List endpoint requires authentication for non-public buckets.")
    def list_buckets(self, search: str = None):
        """List buckets accessible to the current credentials.

        Calls ``GET /v1/buckets`` which returns a lightweight entry per
        bucket — ``name``, ``role``, ``is_public``. The returned
        :class:`Bucket` instances have ``objects_count`` and ``bytes``
        set to ``None`` (call :meth:`get_bucket` to fetch full stats).

        :param search: optional substring filter on bucket name.
        """
        params = {"search": search} if search else None
        resp = self.client.get("/v1/buckets", params=params)
        return [
            Bucket(
                self.client,
                name=entry["name"],
                objects_count=None,
                bytes=None,
                is_public=entry.get("is_public"),
                role=entry.get("role"),
                target="buckets",
            )
            for entry in resp.json()
        ]

    def list(self, search: str = None):
        """Alias for :meth:`list_buckets`."""
        return self.list_buckets(search=search)
