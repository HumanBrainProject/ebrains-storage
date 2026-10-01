"""Structural protocols for the harmonised Drive / Bucket interface.

These :class:`typing.Protocol` definitions describe the surface area that
the EBRAINS Drive (Seafile) and EBRAINS Bucket (Data Proxy) clients have
in common. They are structural: concrete classes such as
:class:`ebrains_drive.repos.Repos`, :class:`ebrains_drive.buckets.Buckets`,
:class:`ebrains_drive.repo.Repo`, :class:`ebrains_drive.bucket.Bucket`,
:class:`ebrains_drive.files.SeafFile`, and
:class:`ebrains_drive.files.DataproxyFile` satisfy these protocols without
needing to inherit from them.

Use the protocols as type hints when writing code that works against
either backend, e.g.::

    def archive(obj: StorageObject) -> bytes:
        return obj.get_content()
"""

from typing import Any, Iterable, Protocol, Union, runtime_checkable


@runtime_checkable
class StorageClient(Protocol):
    """The common surface of :class:`DriveApiClient` and :class:`BucketApiClient`."""

    server: str

    def send_request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class StorageObject(Protocol):
    """A file-like object in either backend."""

    name: str

    def get_content(self) -> bytes: ...

    def get_download_link(self) -> str: ...

    def delete(self) -> Any: ...


@runtime_checkable
class Container(Protocol):
    """A repo (Drive) or bucket (Bucket)."""

    name: str

    def get_file(self, path: str) -> StorageObject: ...

    def upload(self, filelike_or_path: Any, filename: str) -> Any: ...

    def upload_local_file(self, filepath: str, name: Union[str, None] = None, overwrite: bool = False) -> Any: ...

    def delete(self) -> Any: ...

    def is_readonly(self) -> bool: ...


@runtime_checkable
class ContainerManager(Protocol):
    """The collection of containers exposed by a client (``client.repos`` / ``client.buckets``)."""

    def get(self, name: str) -> Container: ...

    def list(self) -> Iterable[Container]: ...

    def create(self, name: str, **kwargs: Any) -> Container: ...

    def delete(self, name: str) -> Any: ...
