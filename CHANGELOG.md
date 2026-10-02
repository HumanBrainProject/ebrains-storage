# Changelog

All notable changes to this project are documented here.
This file starts at version 0.7.0; for earlier releases, see the git tags and the [release history on PyPI](https://pypi.org/project/ebrains-drive/#history).

## 0.7.0 — 2026-10-02

This release harmonises the Drive (Seafile) and Bucket (Data-Proxy) interfaces, so that the same code can work against either backend, and adds resumable multipart upload for large files.
It is backwards compatible: existing code continues to work unchanged.

### Added

Harmonised Drive / Bucket interface:

- `ebrains_drive.connect(..., target="bucket")` returns a `BucketApiClient`; `target="drive"` remains the default.
- `get()`, `list()`, `create()` and `delete()` aliases on both `client.repos` and `client.buckets`,
  so container management reads the same way on either backend.
- `client.buckets.list_buckets(search=None)`, `client.buckets.create_bucket()` and `client.buckets.delete_bucket()`.
- `Bucket.get_dir()`, returning a new `BucketDir` — a virtual directory view over the flat object store, mirroring `SeafDir`.
  Supports `ls(recursive=False)` (using the data-proxy `delimiter` parameter),
  `get_file()`, `get_dir()`, `mkdir()`, `upload()`, `upload_local_file()`, `check_exists()` and `delete(recursive=True)`.
- `Bucket.delete()`, `Bucket.is_readonly()` and `Bucket.upload_local_file()`.
- `Repo.upload()` and `Repo.upload_local_file()` shortcuts for the repo root.
- `SeafFile.get_content(progress=True)`, matching `DataproxyFile.get_content()`.
- `DataproxyFile.copy_to()`, using the data-proxy's native server-side copy endpoint.
- `move_to()` and `copy_to()` snake_case aliases for `moveTo()` and `copyTo()`.
- `client.file` on bucket clients (a new `BucketFile` helper), resolving data-proxy bucket and dataset URLs to file objects.
- `ebrains_drive.base`, defining `StorageClient`, `ContainerManager`, `Container` and `StorageObject` structural protocols for code that works against either backend.

Multipart upload for buckets:

- `Bucket.multipart_upload()` uploads large files in chunks via presigned URLs, and is resumable:
  progress and per-part ETags are checkpointed to a local `<filepath>.multipart_manifest.json`, which is removed on success.
- `Bucket.upload()` switches to multipart automatically for files over 1 GB.
- Both thresholds are configurable through the `EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE` (default 10 MB) and `EBRAINS_DRIVE_MULTIPART_THRESHOLD` (default 1 GB) environment variables.

### Changed

- `BucketApiClient(username=..., password=...)` now authenticates with those credentials.
  Previously they were silently ignored and the client stayed in anonymous public-bucket mode, so later writes failed with a confusing 401.
  `BucketApiClient()` with no arguments still gives anonymous read access to public buckets.

### Deprecated

Both of these still work, and now emit a `DeprecationWarning`:

- `BucketApiClient.create_new()` — use `client.buckets.create_bucket()`.
- `BucketApiClient.delete_bucket()` — use `client.buckets.delete_bucket()` or `bucket.delete()`.

### Fixed

- `Repo.is_readonly()` raised `AttributeError` instead of reporting the permission; it checked a non-existent `perm` attribute rather than `permission`.
- Uploads larger than the data-proxy gateway's 5 GB single-upload limit now succeed, by going through multipart upload.
- `Bucket.upload()` determines the size of a file given by path with `os.path.getsize()`, rather than reading it.
