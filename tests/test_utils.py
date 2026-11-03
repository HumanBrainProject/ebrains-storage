import inspect
import pytest
from ebrains_storage.utils import _multipart_setting, on_401_raise_unauthorized


def generator_fn():
    yield 1


test_401_parameters = [(generator_fn, True), (lambda: 1, False)]


@pytest.mark.parametrize("func,is_generator", test_401_parameters)
def test_on_401_wrap(func, is_generator):
    wrapped_fn = on_401_raise_unauthorized("oh noes")(func)
    assert inspect.isgeneratorfunction(wrapped_fn) == is_generator


multipart_setting_parameters = [
    # new name only, old name only, both (new wins), neither (default)
    ({"EBRAINS_STORAGE_MULTIPART_THRESHOLD": "11"}, 11),
    ({"EBRAINS_DRIVE_MULTIPART_THRESHOLD": "22"}, 22),
    ({"EBRAINS_STORAGE_MULTIPART_THRESHOLD": "33", "EBRAINS_DRIVE_MULTIPART_THRESHOLD": "44"}, 33),
    ({}, 99),
]


@pytest.mark.parametrize("environment,expected", multipart_setting_parameters)
def test_multipart_setting_reads_both_names(environment, expected, monkeypatch):
    """The pre-0.9.0 EBRAINS_DRIVE_* names still work, and the new names take precedence."""
    monkeypatch.delenv("EBRAINS_STORAGE_MULTIPART_THRESHOLD", raising=False)
    monkeypatch.delenv("EBRAINS_DRIVE_MULTIPART_THRESHOLD", raising=False)
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    assert _multipart_setting("MULTIPART_THRESHOLD", 99) == expected
