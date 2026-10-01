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
    # 2.3 or, to talk to the Bucket (Data Proxy) backend:
    bucket_client = ebrains_drive.connect('hbp_username', 'password', target="bucket")


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

    # list buckets you have access to (optionally filter by name substring)
    my_buckets = client.buckets.list_buckets()
    matching = client.buckets.list_buckets(search="atlas")

    # create a new collab + bucket (canonical entry point)
    bucket = client.buckets.create_bucket("new_collab_name")
    # client.create_new(...) still works but is deprecated.

    # upload new file (path or file-like object both accepted)
    bucket.upload("/home/jovyan/test.txt", "test/foobar.txt")
    bucket.upload_local_file("/home/jovyan/test.txt", "test/foobar.txt")

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

    # list the contents (flat)
    files = [f for f in bucket.ls(prefix="test")]

    # or browse as a directory tree (uses the data-proxy `delimiter` parameter)
    root = bucket.get_dir("/")
    for entry in root.ls():
        # entry is either a DataproxyFile (object) or a BucketDir (subprefix)
        print(entry)

    # navigate further
    subdir = root.get_dir("test")
    for entry in subdir.ls():
        print(entry)

    # get the uploaded file
    file_handle = bucket.get_file("foobar.txt")
    file_content = file_handle.get_content()
    # ...with a progress bar:
    file_content = file_handle.get_content(progress=True)

    # native server-side copy (no client-side transfer)
    file_handle.copy_to(dst_name="foobar-backup.txt")

    # delete a bucket (and the wiki associated with it)
    bucket.delete()                # canonical instance method
    client.buckets.delete_bucket("new_collab_name", delete_wiki=True)  # manager-level
    # client.delete_bucket(...) still works but is deprecated.

```

### Harmonised cross-backend interface

The Drive (Seafile) and Bucket (Data-Proxy) clients now share a common
interface so the same code can target either backend:

| concept | Drive | Bucket |
| --- | --- | --- |
| factory | `connect(target="drive")` | `connect(target="bucket")` |
| manager | `client.repos` | `client.buckets` |
| list | `client.repos.list()` / `list_repos()` | `client.buckets.list()` / `list_buckets()` |
| get | `client.repos.get(id)` / `get_repo(id)` | `client.buckets.get(name)` / `get_bucket(name)` |
| create | `client.repos.create(name)` / `create_repo(name)` | `client.buckets.create(name)` / `create_bucket(name)` |
| delete by name | `client.repos.delete(id)` | `client.buckets.delete(name)` / `delete_bucket(name)` |
| container delete | `repo.delete()` | `bucket.delete()` |
| readonly check | `repo.is_readonly()` | `bucket.is_readonly()` |
| upload (root) | `repo.upload(filelike_or_path, name)` / `repo.upload_local_file(path)` | `bucket.upload(filelike_or_path, name)` / `bucket.upload_local_file(path)` |
| directory view | `repo.get_dir("/")` returning `SeafDir` | `bucket.get_dir("/")` returning `BucketDir` |
| download with progress bar | `file.get_content(progress=True)` | `file.get_content(progress=True)` |
| URL helper | `client.file.get_file_by_url(url)` | `client.file.get_file_by_url(url)` |

Structural protocols are also published in `ebrains_drive.base`
(`StorageClient`, `ContainerManager`, `Container`, `StorageObject`) so
backend-agnostic code can be type-checked with `isinstance(...)` at
runtime.

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
