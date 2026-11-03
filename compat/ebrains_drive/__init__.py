"""Deprecated alias for :mod:`ebrains_storage`.

``ebrains_drive`` was renamed to ``ebrains_storage`` in 0.9.0, because the
package has long served both EBRAINS storage services: the Drive (Seafile)
and the Bucket (Data-Proxy). Importing this name still works and gives the
same classes, so existing code needs no change, but it is deprecated.

The aliases registered below bind the *same* module objects as
``ebrains_storage``, not copies, so there is one class per name and
``isinstance`` holds whichever name an object was created through.
"""

import importlib
import sys
import warnings

from ebrains_storage import BucketApiClient, DriveApiClient, connect  # noqa: F401

warnings.warn(
    "'ebrains_drive' has been renamed to 'ebrains_storage'. Importing it still works, but will "
    "stop working in a future release; please use 'import ebrains_storage' instead.",
    FutureWarning,
    stacklevel=2,
)

# Every module of the package, so that `from ebrains_drive.<name> import ...`
# keeps working. `_version` is included because it was importable before.
for _name in (
    "_version",
    "admin",
    "base",
    "bucket",
    "buckets",
    "client",
    "exceptions",
    "file",
    "files",
    "group",
    "repo",
    "repos",
    "utils",
):
    _module = importlib.import_module(f"ebrains_storage.{_name}")
    sys.modules[f"{__name__}.{_name}"] = _module
    globals()[_name] = _module

del _name, _module
