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
		<li><a href="#repo_upload">Upload (library shortcut)</a></li>
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
		<li><a href="#seaffile_move_copy">Move and Copy</a></li>
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
        <li><a href="#bucket_bucket_list">List Buckets</a></li>
        <li><a href="#bucket_bucket_create">Create Bucket</a></li>
        <li><a href="#bucket_bucket_delete">Delete Bucket</a></li>
        <li><a href="#bucket_bucket_is_readonly">Check Bucket Permission</a></li>
        <li><a href="#bucket_bucket_ls">List Bucket Entries (flat)</a></li>
    </ul>
    <li><a href="#bucket_dir">Bucket Directory</a></li>
    <ul>
        <li><a href="#bucket_dir_get">Get Directory</a></li>
        <li><a href="#bucket_dir_ls">List Directory Entries</a></li>
        <li><a href="#bucket_dir_mkdir">Create New Directory</a></li>
        <li><a href="#bucket_dir_delete">Delete Directory</a></li>
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
        <li><a href="#bucket_file_copy">Copy File</a></li>
        <li><a href="#bucket_file_delete">Delete File</a></li>
    </ul>
    <li><a href="#bucket_url_helper">URL Helper</a></li>
</ul>

<li><a href="#harmonised">Cross-backend interface</a></li>
<ul>
    <li><a href="#harmonised_protocols">Protocols</a></li>
    <li><a href="#harmonised_table">Method comparison table</a></li>
</ul>
</ul>
</div>
</p>

# <a id="sea_file"></a> Drive (Seafile)


## <a id="get_client"></a> Get Client ##
**Request Parameters**

* username
* password
* token (optional, supplied instead of password)
* env (optional, one of `""` (default, production), `"int"`, `"dev"`)
* target (optional, `"drive"` (default) or `"bucket"` — selects which backend to talk to)

**Sample Case**

```python

	import ebrains_drive

	# Drive (Seafile) — default target
	client = ebrains_drive.connect('hbp_username', 'password')

	# Or talk to the Bucket (Data Proxy) backend via the same factory
	bucket_client = ebrains_drive.connect('hbp_username', 'password', target="bucket")
```

**Return Type**

A `DriveApiClient` when `target="drive"` (default), a `BucketApiClient`
when `target="bucket"`. For anonymous read access to public buckets,
construct `BucketApiClient()` directly — `connect()` always authenticates.


## <a id="repo"></a> Library ##
### <a id="repo_get_repo"></a> Get Library ###
**Request Parameters**

* repo_id

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    # `client.repos.get(repo_id)` is an alias that mirrors the Bucket surface.
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

`Bucket.is_readonly()` exists with the same signature on the Bucket
backend, so cross-backend code can call `container.is_readonly()`
regardless of which container type it has.

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

    # `client.repos.list()` is an alias for `list_repos()`.
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
    # `client.repos.create('test_repo')` is an alias.
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
    # Equivalently: client.repos.delete('09c16e2a-...').
```

**Return Type**

None

### <a id="repo_upload"></a> Upload (library shortcut) ###

**Request Parameters**

* filelike_or_path (file-like object, `bytes`, or path to a local file)
* filename (name to store the file under, at the root of the library)

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')

    # Path or file-like — both work
    repo.upload('/home/jovyan/notes.md', 'notes.md')
    repo.upload_local_file('/home/jovyan/notes.md', overwrite=True)
```

These are convenience shortcuts for `repo.get_dir("/").upload(...)` and
`repo.get_dir("/").upload_local_file(...)` that mirror
`Bucket.upload` / `Bucket.upload_local_file`.

**Return Type**

A `SeafFile` of the newly uploaded file.

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

* progress (keyword-only, default `False`) — when `True`, stream the
  download and display a `tqdm` progress bar.

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seaffile = repo.get_file('/root/test.md')

    content = seaffile.get_content()
    content = seaffile.get_content(progress=True)  # with progress bar
```

The `progress=` keyword mirrors `DataproxyFile.get_content(progress=...)`
on the Bucket backend.

**Return Type**

`bytes` (file content)

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

`upload_local_file`:
* filepath (path to the local file)
* name (default `None`, defaults to the basename of `filepath`)
* overwrite (default `False`; when `True`, replace an existing file with the same name)

`upload` (polymorphic):
* fileobj — a file-like object, a `bytes` value, or a path/`PathLike`
  (the path overload mirrors `Bucket.upload`)
* filename — the name to store the file under

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seafdir = repo.get_dir('/root')

    # original two-method form
    file = seafdir.upload_local_file('/home/ubuntu/env.md')

    # `upload(...)` now also accepts a path directly
    file = seafdir.upload('/home/ubuntu/env.md', 'env.md')

    # ...and still accepts a file-like object / bytes
    with open('/home/ubuntu/env.md', 'rb') as fp:
        file = seafdir.upload(fp, 'env.md')
```

**Return Type**

A File Object of the uploaded file

**Exception**

* Local file does not exist.
* `FileExistsError` — when `upload_local_file(..., overwrite=False)`
  is called with a name that already exists in the directory.

### <a id="seaffile_move_copy"></a> Move and Copy ###

**Request Parameters**

* dst_dir (destination directory path)
* dst_repo_id (optional; copy/move into another library)

**Sample Case**

```python

    import ebrains_drive

    client = ebrains_drive.connect('hbp_username', 'password')
    repo = client.repos.get_repo('09c16e2a-ff1a-4207-99f3-1351c3f1e507')
    seaffile = repo.get_file('/root/test.md')

    # camelCase (legacy) and snake_case (new) are interchangeable
    seaffile.copyTo('/backup')
    seaffile.copy_to('/backup')
    seaffile.move_to('/archive')
```

**Return Type**

`bool` — `True` on success.


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

* username (optional)
* password (optional)
* token (optional)
* env (optional)

**Sample Case**

```python
    # Direct construction
    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    # Or via the shared factory with target="bucket"
    import ebrains_drive
    client = ebrains_drive.connect(token="ey...", target="bucket")

    # Anonymous read access to public buckets (no token)
    anon = BucketApiClient()
```


**Return Type**

A `BucketApiClient`. `client.buckets` is the bucket manager (mirrors
`client.repos` on the Drive side); `client.file` exposes a URL-resolution
helper (see [URL Helper](#bucket_url_helper)).

## <a id="bucket_bucket"></a> Bucket ##
### <a id="bucket_bucket_get"></a> Get Bucket ###
**Request Parameters**

* existing_collab_name
* public (keyword-only, default `False`)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")
    # `client.buckets.get("existing_collab_name")` is an alias.
```

**Return Type**

A Bucket Object

**Exceptions**

* Bucket does not exist or not authorized to use the specified bucket

### <a id="bucket_bucket_list"></a> List Buckets ###

**Request Parameters**

* search (optional substring filter on bucket name)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    # all buckets the credentials can access
    buckets = client.buckets.list_buckets()
    print([b.name for b in buckets])

    # filter by name substring
    atlas_buckets = client.buckets.list_buckets(search="atlas")
    # `client.buckets.list()` is an alias.
```

The returned `Bucket` objects have `objects_count` and `bytes` set to
`None`. Call `client.buckets.get_bucket(name)` (or `.stat`) to fetch the
full statistics for a specific bucket.

**Return Type**

A list of Bucket Objects (each carrying `name`, `role`, `is_public`).

**Exceptions**

* `Unauthorized` when the credentials cannot enumerate buckets.

### <a id="bucket_bucket_create"></a> Create Bucket ###
**Request Parameters**

* bucket_name
* title (optional, defaults to `bucket_name`)
* description (optional)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    # Canonical entry point
    bucket = client.buckets.create_bucket("new_collab_name")
    # `client.buckets.create("new_collab_name")` is an alias.

    # Legacy form (still works, but emits a DeprecationWarning):
    bucket = client.create_new("new_collab_name")
```

**Return Type**

A Bucket Object

**Exceptions**

* Unauthorized to create new collab or bucket

### <a id="bucket_bucket_delete"></a> Delete Bucket ###

**Request Parameters**

* bucket_name
* delete_wiki (keyword-only, default `False`; when `True`, also delete the
  associated wiki/collab)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    # Three equivalent ways to delete a bucket:
    client.buckets.delete_bucket("name")                  # canonical, manager-level
    client.buckets.delete("name", delete_wiki=True)       # alias of delete_bucket
    client.buckets.get_bucket("name").delete()            # instance method on Bucket
    # Legacy `client.delete_bucket("name")` still works but emits a
    # DeprecationWarning.
```

**Return Type**

None

**Exceptions**

* `Unauthorized` when the credentials cannot delete the bucket.

### <a id="bucket_bucket_is_readonly"></a> Check Bucket Permission ###

**Request Parameters**

None

**Sample Case**

```python

    bucket = client.buckets.get_bucket("existing_collab_name")
    if bucket.is_readonly():
        ...
```

Returns `True` when `bucket.role` is `None` or `"viewer"`; `False` for
`"editor"` and `"administrator"`. Dataset buckets and anonymously
accessed public buckets conservatively report read-only. Mirrors
`Repo.is_readonly()` so cross-backend code can use a single check.

**Return Type**

Boolean

### <a id="bucket_bucket_ls"></a> List Bucket Entries (flat) ###
**Request Parameters**

* prefix (optional)

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")

    # shows all files (flat, no directory grouping)
    all_files = [f for f in bucket.ls()]

    # shows all files whose name begins with path/to/my/files
    my_files = [f for f in bucket.ls(prefix="path/to/my/files")]
```

For a tree-style view that groups objects by `/` boundaries, use
[Bucket Directory](#bucket_dir) instead.

**Return Type**

An Iterator of `DataproxyFile` Objects

**Exceptions**

* Unauthorized

## <a id="bucket_dir"></a> Bucket Directory ##

The data-proxy backend is a flat object store, but `BucketDir` exposes
the same prefix-as-directory tree view that the DataProxy GUI uses, so
the same code that works against `SeafDir` can target buckets too.
`BucketDir.ls()` issues a request with the native `delimiter` parameter
so the server returns grouped sub-prefixes — efficient even for large
buckets.

### <a id="bucket_dir_get"></a> Get Directory ###

**Request Parameters**

* path (`"/"` returns the bucket root)

**Sample Case**

```python

    bucket = client.buckets.get_bucket("existing_collab_name")

    root = bucket.get_dir("/")              # bucket root
    nested = bucket.get_dir("/path/inside") # arbitrary prefix
    deeper = root.get_dir("path").get_dir("inside")  # chained navigation
```

No HTTP round-trip is made — listing happens lazily.

**Return Type**

A `BucketDir` Object

### <a id="bucket_dir_ls"></a> List Directory Entries ###

**Request Parameters**

* recursive (keyword-only, default `False`)
  * `False` — yield only the immediate children of this prefix. Each
    entry is either a `BucketDir` (a sub-prefix) or a `DataproxyFile`
    (an object directly under this prefix).
  * `True` — yield every `DataproxyFile` under this prefix at any depth.

**Sample Case**

```python

    root = bucket.get_dir("/")

    # Tree view: subdirectories + files at this level
    for entry in root.ls():
        print(entry)
    # BucketDir[bucket=foo, path=/dir1]
    # BucketDir[bucket=foo, path=/dir2]
    # DataproxyFile[bucket=foo, path=top.txt, size=12]

    # Or flatten everything under this prefix:
    all_files = list(root.ls(recursive=True))
```

**Return Type**

An iterator of `BucketDir` and `DataproxyFile` (or just `DataproxyFile`
when `recursive=True`).

### <a id="bucket_dir_mkdir"></a> Create New Directory ###

**Request Parameters**

* name

**Sample Case**

```python

    root = bucket.get_dir("/")
    new_dir = root.mkdir("future")
```

**Note:** object-storage directories exist purely by convention — they
spring into existence when an object is uploaded under that prefix.
`mkdir` therefore performs **no HTTP request** and changes no
server-side state; it simply returns a new `BucketDir` for the named
sub-prefix.

**Return Type**

A `BucketDir` Object

### <a id="bucket_dir_delete"></a> Delete Directory ###

**Request Parameters**

* recursive (keyword-only, required; must be `True` to perform the deletion)

**Sample Case**

```python

    bucket.get_dir("/sub").delete(recursive=True)
```

This deletes every object under the prefix. Calling `delete()` without
`recursive=True` raises `OperationError` — the explicit opt-in is
deliberate because there is no undo.

**Return Type**

None

**Exceptions**

* `OperationError` — when called without `recursive=True`.

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

Files in buckets are objects in a flat namespace. Names commonly contain
`/` to encode a directory-like structure; see
[Bucket Directory](#bucket_dir) for a tree-style API over that
convention.


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

* progress (keyword-only, default `False`) — when `True`, stream the
  download and display a `tqdm` progress bar.

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")

    bucket = client.buckets.get_bucket("existing_collab_name")
    # OR
    bucket = client.buckets.get_dataset("dataset_id")

    file_handle = bucket.get_file("filename")
    file_content = file_handle.get_content()
    file_content = file_handle.get_content(progress=True)  # with progress bar
```

`SeafFile.get_content(progress=...)` exists with the same signature on
the Drive backend.

**Return Type**

bytes

**Exceptions**

* Unauthorized
* DoesNotExist


### <a id="bucket_file_upload"></a> Upload File ###

**`Bucket.upload`** is polymorphic — its first argument may be a path
(`str`/`PathLike`) or a file-like object. **`Bucket.upload_local_file`**
is the strict path-based variant (mirrors `SeafDir.upload_local_file`).

**Request Parameters**

`upload`:
* filelike — file-like object, `bytes`, or path to a local file
* filename — name to store the file under in the bucket
* `**kwargs` — passed through to the underlying request (e.g. `headers=`)

`upload_local_file`:
* filepath — path to the local file
* name (optional) — destination object name; defaults to the basename
  of `filepath`
* overwrite (default `False`) — when `False`, raise `FileExistsError`
  if an object with that name already exists

**Sample Case**

```python

    from ebrains_drive import BucketApiClient
    client = BucketApiClient(token="ey...")
    bucket = client.buckets.get_bucket("existing_collab_name")

    # Path or file-like — both work
    bucket.upload("/home/jovyan/test.txt", "test/foobar.txt")

    from io import StringIO
    fh = StringIO("hello world")
    fh.seek(0)
    bucket.upload(fh, "test/foobar.txt")

    # Path-only variant with overwrite control
    bucket.upload_local_file("/home/jovyan/test.txt", "test/foobar.txt", overwrite=True)
```

**Return Type**

None

**Exceptions**

* Unauthorized
* `FileExistsError` from `upload_local_file(..., overwrite=False)` when
  the destination name is already used.

### <a id="bucket_file_copy"></a> Copy File ###

Server-side copy — no client-side data transfer. Uses the data-proxy's
native `PUT /v1/buckets/{name}/{object}/copy` endpoint.

**Request Parameters** (at least one must be supplied)

* dst_name — destination object name (within the same bucket, unless
  `dst_bucket` is also set)
* dst_bucket (keyword-only) — destination bucket name

**Sample Case**

```python

    bucket = client.buckets.get_bucket("existing_collab_name")
    f = bucket.get_file("report.csv")

    # Copy within the same bucket under a new name
    f.copy_to(dst_name="report-backup.csv")

    # Copy to a different bucket (same name)
    f.copy_to(dst_bucket="archive-bucket")

    # Copy to a different bucket under a new name
    f.copy_to(dst_name="report-archived.csv", dst_bucket="archive-bucket")
```

**Return Type**

`bool` — `True` on success.

**Exceptions**

* `ValueError` — when neither `dst_name` nor `dst_bucket` is supplied.
* Unauthorized

### <a id="bucket_file_delete"></a> Delete File ###
**Request Parameters**

None

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

## <a id="bucket_url_helper"></a> URL Helper

`BucketApiClient.file` exposes a URL-resolution helper analogous to
`DriveApiClient.file`. Pass a data-proxy URL and get back a
`DataproxyFile`:

```python

    client = BucketApiClient(token="ey...")

    f = client.file.get_file_by_url(
        "https://data-proxy.ebrains.eu/api/v1/buckets/my-bucket/path/to/file.txt"
    )

    # Dataset URLs are supported too
    f = client.file.get_file_by_url(
        "https://data-proxy.ebrains.eu/api/v1/datasets/<dataset_id>/path/to/file"
    )
```

**Return Type**

A `DataproxyFile`.

**Exceptions**

* `ValueError` — when the URL does not match the expected data-proxy format.

# <a id="harmonised"></a> Cross-backend interface

The Drive (Seafile) and Bucket (Data-Proxy) clients share a harmonised
surface so the same code can target either backend.

## <a id="harmonised_protocols"></a> Protocols

`ebrains_drive.base` defines four runtime-checkable `typing.Protocol`s
that both backends satisfy structurally (no inheritance required):

* `StorageClient` — `DriveApiClient`, `BucketApiClient`
* `ContainerManager` — `Repos`, `Buckets`
* `Container` — `Repo`, `Bucket`
* `StorageObject` — `SeafFile`, `DataproxyFile`

```python
    from ebrains_drive.base import Container, StorageObject

    def archive(container: Container, name: str) -> bytes:
        obj: StorageObject = container.get_file(name)
        return obj.get_content()

    # Works against either backend
    archive(repo, "/notes.md")
    archive(bucket, "notes.md")

    # isinstance() against the Protocol works at runtime
    assert isinstance(bucket, Container)
```

## <a id="harmonised_table"></a> Method comparison table

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
| upload (container shortcut) | `repo.upload(filelike_or_path, name)` / `repo.upload_local_file(path)` | `bucket.upload(filelike_or_path, name)` / `bucket.upload_local_file(path)` |
| directory view | `repo.get_dir("/")` → `SeafDir` | `bucket.get_dir("/")` → `BucketDir` |
| download w/ progress | `file.get_content(progress=True)` | `file.get_content(progress=True)` |
| server-side copy | `file.copy_to(dst_dir)` / `copyTo(...)` | `file.copy_to(dst_name=..., dst_bucket=...)` |
| URL helper | `client.file.get_file_by_url(url)` | `client.file.get_file_by_url(url)` |

The legacy `BucketApiClient.create_new` / `BucketApiClient.delete_bucket`
methods still work but emit a `DeprecationWarning` pointing to the
canonical `client.buckets.create_bucket` / `client.buckets.delete_bucket`
calls.
