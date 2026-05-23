"""
A Python package for working with the Human Brain Project Model Validation Framework.

Andrew Davison and Shailesh Appukuttan, CNRS, 2017-2020

License: BSD 3-clause, see LICENSE.txt

"""

from ebrains_drive.client import DriveApiClient, BucketApiClient


def connect(username=None, password=None, token=None, env="", target="drive"):
    """Return an authenticated EBRAINS client.

    :param target: ``"drive"`` (default) returns a
        :class:`ebrains_drive.client.DriveApiClient`; ``"bucket"`` returns
        a :class:`ebrains_drive.client.BucketApiClient`. The default
        preserves backwards compatibility.

    For anonymous read access to public buckets, construct
    :class:`BucketApiClient` directly rather than going through this
    factory: ``connect()`` always authenticates.
    """
    if target == "drive":
        return DriveApiClient(username, password, token, env)
    if target == "bucket":
        return BucketApiClient(username, password, token, env)
    raise ValueError(f"Unknown target: {target!r}. Expected 'drive' or 'bucket'.")
