import inspect
import pytest
from ebrains_drive.utils import on_401_raise_unauthorized


def generator_fn():
    yield 1


test_401_parameters = [(generator_fn, True), (lambda: 1, False)]


@pytest.mark.parametrize("func,is_generator", test_401_parameters)
def test_on_401_wrap(func, is_generator):
    wrapped_fn = on_401_raise_unauthorized("oh noes")(func)
    assert inspect.isgeneratorfunction(wrapped_fn) == is_generator
