import string
import random
import inspect
from functools import wraps
from typing import Type
from urllib.parse import urlencode
from ebrains_drive.exceptions import ClientHttpError, DoesNotExist, Unauthorized


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
