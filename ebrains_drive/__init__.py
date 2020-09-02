"""
A Python package for working with the Human Brain Project Model Validation Framework.

Andrew Davison and Shailesh Appukuttan, CNRS, 2017-2020

License: BSD 3-clause, see LICENSE.txt

"""

from ebrains_drive.client import DriveApiClient

def connect(username=None, password=None, token=None, env=""):
    client = DriveApiClient(username, password, token, env)
    return client