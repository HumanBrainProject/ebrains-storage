"""
A Python package for working with the Human Brain Project Model Validation Framework.

Andrew Davison and Shailesh Appukuttan, CNRS, 2017-2020

License: BSD 3-clause, see LICENSE.txt

"""

from hbp_seafile.client import SeafileApiClient

def connect(username=None, password=None, token=None, server="https://drive.ebrains.eu"):
    client = SeafileApiClient(username, password, token, server)
    return client