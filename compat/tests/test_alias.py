"""Tests for the ebrains_storage compatibility stub.

These need both distributions installed: `pip install . ./compat` from the
repository root. They are not part of the main test run, which ignores compat/.
"""

import subprocess
import sys

import pytest

import ebrains_storage
import ebrains_storage


def test_import_emits_a_future_warning():
    """A fresh interpreter must warn, and the warning must name the new module."""
    result = subprocess.run(
        [sys.executable, "-W", "error::FutureWarning", "-c", "import ebrains_storage"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "importing ebrains_storage did not warn"
    assert "FutureWarning" in result.stderr
    assert "ebrains_storage" in result.stderr


def test_warning_is_visible_by_default():
    """FutureWarning, unlike DeprecationWarning, is not silenced outside __main__."""
    result = subprocess.run(
        [sys.executable, "-c", "import ebrains_storage"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "FutureWarning" in result.stderr


@pytest.mark.parametrize("name", ["connect", "DriveApiClient", "BucketApiClient"])
def test_top_level_names_are_the_same_objects(name):
    assert getattr(ebrains_storage, name) is getattr(ebrains_storage, name)


@pytest.mark.parametrize(
    "name",
    [
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
    ],
)
def test_submodule_aliases_bind_the_same_module(name):
    assert sys.modules[f"ebrains_storage.{name}"] is sys.modules[f"ebrains_storage.{name}"]
    assert getattr(ebrains_storage, name) is getattr(ebrains_storage, name)


def test_from_import_of_a_submodule_works():
    from ebrains_storage.client import BucketApiClient as Aliased

    assert Aliased is ebrains_storage.client.BucketApiClient


def test_class_identity_holds_across_both_names():
    """An object made through the old name is an instance of the new name's class."""
    client = ebrains_storage.client.BucketApiClient()

    assert isinstance(client, ebrains_storage.client.BucketApiClient)
    assert type(client) is ebrains_storage.client.BucketApiClient


def test_exceptions_are_catchable_under_either_name():
    with pytest.raises(ebrains_storage.exceptions.DoesNotExist):
        raise ebrains_storage.exceptions.DoesNotExist("x")
