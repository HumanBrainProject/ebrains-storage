import string
import random
import inspect
from functools import wraps
from typing import Type
from urllib.parse import urlencode
import os

from ebrains_storage.exceptions import ClientHttpError, DoesNotExist, Unauthorized


def randstring(length=0):
    if length == 0:
        length = random.randint(1, 30)
    return "".join(random.choice(string.lowercase) for i in range(length))


def _raise_on(http_code: int, Ex: Type[Exception]):
    """Decorator factory funciton to turn a function that get a http http_code response
    to a `Ex` exception."""

    def raise_on(msg: str):
        def decorator(func):

            if inspect.isgeneratorfunction(func):

                @wraps(func)
                def wrapped(*args, **kwargs):
                    try:
                        yield from func(*args, **kwargs)
                    except ClientHttpError as e:
                        if e.code == http_code:
                            raise Ex(msg)
                        else:
                            raise e

                return wrapped

            else:

                @wraps(func)
                def wrapped(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except ClientHttpError as e:
                        if e.code == http_code:
                            raise Ex(msg)
                        else:
                            raise e

                return wrapped

        return decorator

    return raise_on


on_401_raise_unauthorized = _raise_on(401, Unauthorized)


def raise_does_not_exist(msg):
    """Decorator to turn a function that get a http 404 response to a
    :exc:`DoesNotExist` exception."""

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientHttpError as e:
                if e.code == 404:
                    raise DoesNotExist(msg)
                else:
                    raise

        return wrapped

    return decorator


def to_utf8(obj):
    if isinstance(obj, str):
        return obj.encode("utf-8")
    return obj


def querystr(**kwargs):
    return "?" + urlencode(kwargs)


# not used?
def utf8lize(obj):
    if isinstance(obj, dict):
        return {k: to_utf8(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [to_utf8(x) for x in ob]

    if instance(obj, str):
        return obj.encode("utf-8")

    return obj

def _multipart_setting(name: str, default: int) -> int:
    """Read one of the multipart settings from the environment.

    The settings were named EBRAINS_DRIVE_* before the package was renamed in
    0.9.0. The old name is still read, so that existing deployment
    configuration keeps working; the new name wins when both are set.
    """
    value = os.getenv(f"EBRAINS_STORAGE_{name}") or os.getenv(f"EBRAINS_DRIVE_{name}")
    return int(value) if value else default


EBRAINS_STORAGE_MULTIPART_CHUNK_SIZE = _multipart_setting("MULTIPART_CHUNK_SIZE", 10 * 1024 * 1024)
"""Chunk size of mulitpart upload. Doubles as a lower threshold for qualifying for multipart upload. (default: 10M)

n.b. there is an undocumented lower hard threshold for multipart upload of 5M"""

EBRAINS_STORAGE_MULTIPART_THRESHOLD = _multipart_setting("MULTIPART_THRESHOLD", 1024 * 1024 * 1024)
"""Upper threshold for uploading large blob of file (default: 1G) Over which, multipart upload will be used..

n.b. there is an undocumented upper hard threshold for single upload of 5G"""

# Deprecated aliases under the pre-0.9.0 names, kept so that code importing them
# from this module keeps working.
EBRAINS_DRIVE_MULTIPART_CHUNK_SIZE = EBRAINS_STORAGE_MULTIPART_CHUNK_SIZE
EBRAINS_DRIVE_MULTIPART_THRESHOLD = EBRAINS_STORAGE_MULTIPART_THRESHOLD
