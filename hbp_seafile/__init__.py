"""
A Python package for working with the Human Brain Project Model Validation Framework.

Andrew Davison and Shailesh Appukuttan, CNRS, 2017-2020

License: BSD 3-clause, see LICENSE.txt

"""

from seafileapi.client import SeafileApiClient

def connect(server, username, password):
    client = SeafileApiClient(server, username, password)
    return client
