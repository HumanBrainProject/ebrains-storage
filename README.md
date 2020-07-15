hbp_seafile
==============

Python client interface for HBP Collaboratory Seafile storage


Original implementation source:
https://github.com/haiwen/python-seafile
by Shuai Lin (linshuai2012@gmail.com)


Updated for integration with HBP v2 Collaboratory's Seafile storage
by Shailesh Appukuttan (appukuttan.shailesh@gmail.com)


Documentation: https://github.com/appukuttan-shailesh/hbp-seafile/blob/master/doc.md

Installation: `pip install hbp_seafile`


Example usage (refer to docs for more):

```python
    # 1. import module
    import hbp_seafile

    # 2. create client object
    # 2.1 either via
    client = hbp_seafile.connect('hbp_username', 'password')
    # 2.2 or via
    from hbp_seafile.client import SeafileApiClient
    client = SeafileApiClient(username="hbp_username", password="password")


```


<div><img src="https://raw.githubusercontent.com/appukuttan-shailesh/hbp-seafile/master/eu_logo.jpg" alt="EU Logo" width="15%" align="right"></div>

### ACKNOWLEDGEMENTS
This open source software code was developed in part in the Human Brain Project, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under Specific Grant Agreements No. 720270 and No. 785907 (Human Brain Project SGA1 and SGA2).