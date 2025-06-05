ebrains_storage
===============

Python client interface for EBRAINS Collaboratory Drive (Seafile) and Bucket (Data-Proxy) storage.


Original implementation source:
https://github.com/haiwen/python-seafile
by Shuai Lin (linshuai2012@gmail.com)


Updated for integration with HBP v2 Collaboratory's Seafile storage (now EBRAINS Drive)
by Shailesh Appukuttan (appukuttan.shailesh@gmail.com)

Updated with support for EBRAINS Bucket storage by Xiao Gui.

Documentation: https://github.com/HumanBrainProject/ebrains-storage/blob/master/doc.md

Installation: `pip install ebrains_drive`


Example usage (refer to docs for more):

```python
    # 1. Import module
    import ebrains_drive

    # 2. Create client object
    # 2.1 either via
    client = ebrains_drive.connect('hbp_username', 'password')
    # 2.2 or via
    from ebrains_drive.client import DriveApiClient
    client = DriveApiClient(username="hbp_username", password="password")


    # 3. Working with Collab drives (libraries / repos)
    # 3.1 Get list of all libraries that user has access to
    list_repos =  client.repos.list_repos()
    # 3.2 Get info of specific library
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    print(repo_obj.__dict__)

    # 4. Working with directories
    # 4.1 Get info of a directory
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    dir_obj = repo_obj.get_dir('/') # specify dir path; '/' signifies root directory
    print(dir_obj.__dict__)
    # 4.2 Get contents of directory
    dir_obj.ls()


    # 5. Working with files
    # 5.1 Get info of a file
    repo_obj = client.repos.get_repo('0fee1620-062d-4643-865b-951de1eee355')
    file_obj = repo_obj.get_file('/sample-latest.csv') # specify file path
    print(file_obj.__dict__)
    # 5.2 Get file content
    file_content = file_obj.get_content()
    print(file_content)
```

## Experimental support for data-proxy

Original implementation from Bjorn Kindler & Jan Fousek.

Example Usage:

### Access collab bucket

```python
    from ebrains_drive import BucketApiClient

    # username/password not supported for bucket yet
    client = BucketApiClient(token="ey...")

    # access existing bucket
    bucket = client.buckets.get_bucket("existing_collab_name")

    # or create a new collab + bucket
    bucket = client.create_new("new_collab_name")

    # upload new file
    bucket.upload("/home/jovyan/test.txt", "test/foobar.txt")

    # Or upload from from in memory:
    from io import StringIO
    fh = StringIO()
    fh.write("hello world")
    fh.seek(0)
    bucket.upload(fh, "test/foobar2.txt")

    # Advanced: specify headers to optimise the stored objects
    import gzip
    from io import BytesIO
    fh = BytesIO(gzip.compress(b"foo bar"))
    fh.seek(0)
    # Most HTTP libraries can handle Content-Encoding header
    bucket.upload(fh, "test/foobar2_gzipped.txt", headers={"Content-Encoding": "gzip"})

    # it seems newly uploaded file will **NOT** be available immediately. Sleep for x seconds?
    from time import sleep
    sleep(1)

    # list the contents
    files = [f for f in bucket.ls(prefix="test")]

    # get the uploaded file
    file_handle = bucket.get_file("foobar.txt")
    file_content = file_handle.get_content()

    # delete a bucket, and also delete the wiki associated with it)
    client.delete_bucket("new_collab_name", delete_wiki=True)

```

Read access of public buckets can be done without supplying a token:

```python

    from ebrains_drive import BucketApiClient

    # anonymous client only has read access to public buckets
    anon_client = BucketApiClient()
    public_bucket = anon_client.buckets.get_bucket("reference-atlas-data")

    # list all files under static/
    files = public_bucket.ls(prefix="static")
    print([f.name for f in files])

```

### Access datasets (e.g. HDG datasets)

```python
    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    # access dataset bucket
    # setting requeste_access = True will start the relevant access-request-flow when accessing HDG datasets
    bucket = client.buckets.get_dataset("existing_dataset_id", request_access=True)

    # list the contents
    files = [f for f in bucket.ls(prefix="path/to/somewhere/foo")]

    # get a file content
    file_handle = bucket.get_file("path/to/somewhere/foobar.txt")
    file_content = file_handle.get_content()

```

<div><img src="https://raw.githubusercontent.com/HumanBrainProject/ebrains-drive/master/eu_logo.jpg" alt="EU Logo" width="15%" align="right"></div>

### ACKNOWLEDGEMENTS
This open source software code was developed in part in the Human Brain Project, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under Specific Grant Agreements No. 720270,  No. 785907, and No. 945539 (Human Brain Project SGA1, SGA2 and SGA3), and by the European Union's Research and Innovation Program Horizon Europe Grant Agreement No. 101147319 (EBRAINS 2.0).
