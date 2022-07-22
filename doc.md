# Ebrains Drive
<p><div class="doc">
<ul>
<li><a href="#sea_file">Drive (Seafile)</a></li>
<ul>
<li><a href="#get_client">Get Client</a></li>
<li>
	<a href="#repo"> Library </a>
	<ul>
		<li><a href="#repo_get_repo">Get Library</a></li>
		<li><a href="#repo_is_readonly">Check Library Permission</a></li>
		<li><a href="#repo_list_repo">List all Libraries</a></li>
		<li><a href="#repo_create_repo">Create Library</a></li>
		<li><a href="#repo_delete">Delete Library</a></li>
	</ul>
</li>
<li>
	<a href="#seafdir">Directory</a>
	<ul>
		<li><a href="#seafdir_get">Get Directory</a></li>
		<li><a href="#seafdir_ls">List Directory Entries</a></li>
		<li><a href="#seafdir_mkdir">Create New Directory</a></li>
		<li><a href="#seafdir_download">Download Directory</a></li>
		<li><a href="#seafdir_delete">Delete Directory</a></li>
	</ul>
</li>
<li>
	<a href="#seaffile">File</a>
	<ul>
		<li><a href="#seaffile_get">Get File</a></li>
		<li><a href="#seaffile_get_content">Get Content</a></li>
		<li><a href="#seaffile_create_empty_file">Create Empty File</a></li>
		<li><a href="#seaffile_upload_file">Upload File</a></li>
		<li><a href="#seaffile_delete">Delete file</a></li>
	</ul>
</li>
</ul>

<li><a href="#bucket">DataProxy</a></li>
<ul>
    <li><a href="#bucket_get_client">Get Client</a></li>
    <li><a href="#bucket_bucket">Bucket</li>
    <ul>
        <li><a href="#bucket_bucket_get">Get Bucket</a></li>
        <li><a href="#bucket_bucket_create">Create Bucket</a></li>
        <li><a href="#bucket_bucket_ls">List Bucket Entries</a></li>
    </ul>
    <li><a href="#bucket_dataset">Dataset</a></li>
    <ul>
        <li><a href="#bucket_dataset_get">Get Dataset</a></li>
    </ul>
    <li><a href="#bucket_file">File</a></li>
    <ul>
        <li><a href="#bucket_file_get">Get File</a></li>
        <li><a href="#bucket_file_get_content">Get Content</a></li>
        <li><a href="#bucket_file_upload">Upload File</a></li>
        <li><a href="#bucket_file_delete">Delete File</a></li>
    </ul>
</ul>
</ul>
</div>
</p>

# <a id="sea_file"></a> Drive (Seafile)


## <a id="get_client"></a> Get Client ##
**Request Parameters**

* server
* username
* password

**Sample Case**

```python

	import ebrains_drive
	
	client = ebrains_drive.connect('hbp_username', 'password')
```

**Return Type**

A Client Object


## <a id="repo"></a> Library ##
### <a id="repo_get_repo"></a> Get Library ###
**Request Parameters**

* repo_id

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
```

**Return Type**

A Library Object

**Exception**

* Library does not exist.

### <a id="repo_is_readonly"></a> Check Library Permission ###

**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    is_readonly = repo.is_readonly()
```

**Return Type**

Boolean

### <a id="repo_list_repo"></a> List all Libraries ###

**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo_list = client.repos.list_repos()

    print(repo_list)
    Out >>> [<ebrains_drive.repo.Repo at 0x7f1bb0769750>,
             <ebrains_drive.repo.Repo at 0x7f1bb07693d0>,
             <ebrains_drive.repo.Repo at 0x7f1bb0769a50>,
             <ebrains_drive.repo.Repo at 0x7f1bb077cc10>,
             <ebrains_drive.repo.Repo at 0x7f1bb077cfd0>,
             <ebrains_drive.repo.Repo at 0x7f1bb077ca10>]

    print([repo.name for repo in repo_list])
    Out >>> ['alphabox',
             'hello',
             'Doc',
             'obj_test',
             'fs_test',
             'global']
```

**Return Type**

A list of Libraries Object

### <a id="repo_create_repo"></a> Create Library ###

**Request Parameters**

* name
* password (default None)

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.create_repo('test_repo')
```

**Return Type**

A Library Object


### <a id="repo_delete"></a> Delete Library ###

**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    repo.delete()
```

**Return Type**

None

## <a id="seafdir"></a> Directory ##
### <a id="seafdir_get"></a> Get Directory ###

**Request Parameters**

* path

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
    print(seafdir.__dict__)
    Out >>> {'client': DriveApiClient[server=http://127.0.0.1:8000, user=admin@admin.com],
             'entries': [],
             'id': 'c3742dd86004d51c358845fa3178c87e4ab3aa60',
             'path': '/root',
             'repo': <ebrains_drive.repo.Repo at 0x7f2af56b1490>,
             'size': 0}
```

**Return Type**

A Directory Object

**Exception**

* Directory does not exist.

### <a id="seafdir_ls"></a> List Directory Entries ###
**Request Parameters**

* force_refresh (default False)

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
	
    lst = seafdir.ls(force_refresh=True)
    print(lst)
    Out >>> [SeafDir[repo=01ccc4,path=/Seahub/6.1.x,entries=14],
             SeafDir[repo=01ccc4,path=/Seahub/6.2.2-pro,entries=1],
             SeafDir[repo=01ccc4,path=/Seahub/6.2.3,entries=15],
             SeafDir[repo=01ccc4,path=/Seahub/6.2.x,entries=5],
             SeafFile[repo=01ccc4,path=/Seahub/.DS_Store,size=6148],
             SeafFile[repo=01ccc4,path=/Seahub/error.md,size=127],
             SeafFile[repo=01ccc4,path=/Seahub/preview-research.md,size=1030]]

    print([dirent.name for dirent in lst])
    Out >>> ['6.1.x',
             '6.2.2-pro',
             '6.2.3',
             '6.2.x',
             '.DS_Store',
             'error.md',
             'preview-research.md']
```

**Return Type**

List of Directory and File


### <a id="seafdir_mkdir"></a> Create New Directory ###
**Request Parameters**

* name

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
	
    new_dir = seafdir.mkdir('tmp_dir')
```

**Return Type**

A Directory Object of new directory


### <a id="seafdir_download"></a> Download Directory ###
**Request Parameters**

* name (optional)

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')

    # download the entire repository
    base_dir = repo.get_dir('/')
    base_dir.download()

    # download a directory
    my_dir = repo.get_dir("/d1/d2/dir2_1")
    my_dir.download(name="somename.zip")
```

**Return Type**

A Directory Object


### <a id="seafdir_delete"></a> Delete Directory ###
**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
	
    seafdir.delete()
```

**Return Type**

A Response Instance


## <a id="seaffile"></a> File ##
### <a id="seaffile_get"></a> Get File ###

**Request Parameters**

* path

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seaffile = repo.get_file('/root/test.md')

    print(seafile.__dict__)
    Out >>> {'client': DriveApiClient[server=http://127.0.0.1:8000, user=admin@admin.com],
             'id': '0000000000000000000000000000000000000000',
             'path': '/root/test.md',
             'repo': <ebrains_drive.repo.Repo at 0x7f2af56b1490>,
             'size': 0}
```

**Return Type**

A File Object

**Exception**

* File does not exist.

### <a id="seaffile_get_content"></a> Get Content ###

**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seaffile = repo.get_file('/root/test.md')
	
    content = seaffile.get_content()
```

**Return Type**

File Content

### <a id="seaffile_create_empty_file"></a> Create Empty File ###
**Request Parameters**

* name

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
	
    new_file = seafdir.create_empty_file('tmp_file.md')
```

**Return Type**

A File Object of new empty file


### <a id="seaffile_upload_file"></a> Upload File ###
**Request Parameters**

* filepath
* name (default None, default use local file name)

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')
	
    file = seafdir.upload_local_file('/home/ubuntu/env.md')
```

**Return Type**

A File Object of upload file

**Exception**

* Local file does not exist.


### <a id="seaffile_delete"></a> Delete a file ###
**Request Parameters**

None

**Sample Case**

```python

    import ebrains_drive
	
    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seaffile = repo.get_file('/root/test.md')
	
    seaffile.delete()
```

**Return Type**

A Response Instance



# <a id="bucket"></a> Bucket

## <a id ="bucket_get_client"></a> Get Client
**Request Parameters**

* token

**Sample Case**

```python
    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
```


**Return Type**

A Client Object

## <a id="bucket_bucket"></a> Bucket ##
### <a id="bucket_bucket_get"></a> Get Bucket ###
**Request Parameters**

* existing_collab_name

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")
```

**Return Type**

A Bucket Object

**Exceptions**

* Bucket does not exist or not authorized to use the specified bucket

### <a id="bucket_bucket_create"></a> Create Bucket ###
**Request Parameters**

* new_collab_name

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.create_new("new_collab_name")
```

**Return Type**

A Bucket Object

**Exceptions**

* Unauthorized to create new collab or bucket

### <a id="bucket_bucket_ls"></a> List Bucket Entries ###
**Request Parameters**

* prefix (optional)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")

    # shows all files
    all_files = [f for f in bucket.ls()]

    # shows all files that begins with path/to/my/files
    my_files = [f for f in bucket.ls(prefix="path/to/my/files")]
```

**Return Type**

An Iterator of File Objects

**Exceptions**

* Unauthorized

## <a id="bucket_dataset"></a> Dataset ##
### <a id="bucket_dataset_get"></a> Get Dataset ###

Note, if _request_access_ is set to `True`, this method may require user interaction.

**Request Parameters**

* dataset_id
* request_access (optional, default `False`)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_dataset("dataset_id")
    
```

**Return Type**
A Bucket Object

**Exceptions**

* Unauthorized (if _request_access_ is not set)

## <a id="bucket_file"></a> File ##

Files in buckets are not typically organised in directories. Users may use the `/` in filename to construct a directory-like structure.


### <a id="bucket_file_get"></a> Get File ###
**Request Parameters**

* filename

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    bucket = client.buckets.get_bucket("existing_collab_name")
    # OR
    bucket = client.buckets.get_dataset("dataset_id")

    file_handle = bucket.get_file("filename")

```

**Return Type**

A File Object

**Exceptions**

* Unauthorized
* DoesNotExist

### <a id="bucket_file_get_content"></a> Get File Content ###
**Request Parameters**

* filename

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    bucket = client.buckets.get_bucket("existing_collab_name")
    # OR
    bucket = client.buckets.get_dataset("dataset_id")

    file_handle = bucket.get_file("filename")
    file_content = file_handle.get_content()

```

**Return Type**

bytes

**Exceptions**

* Unauthorized
* DoesNotExist


### <a id="bucket_file_upload"></a> Upload File ###
**Request Parameters**

* path_to_file
* dest_filename

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")

    bucket.upload("path_to_file", "dest_filename")

```

**Return Type**

None

**Exceptions**

* Unauthorized

### <a id="bucket_file_delete"></a> Delete File ###
**Request Parameters**

* filename

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")

    file_handle = bucket.get_file("filename")
    file_handle.delete()

```

**Return Type**

None

**Exceptions**

* Unauthorized
* DoesNotExist
* AssertionError
