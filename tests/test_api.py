import inspect
from unittest import mock

import pytest

import zulu


parametrize = pytest.mark.parametrize


@parametrize(
    "api_func, target_func, args",
    [
        (zulu.now, "zulu.Zulu.now", ()),
        (zulu.parse, "zulu.Zulu.parse", (mock.DEFAULT,)),
        (zulu.range, "zulu.Zulu.range", (mock.DEFAULT, mock.DEFAULT, mock.DEFAULT)),
        (zulu.span_range, "zulu.Zulu.span_range", (mock.DEFAULT, mock.DEFAULT, mock.DEFAULT)),
        (zulu.parse_delta, "zulu.delta.Delta.parse", (mock.DEFAULT,)),
    ],
)
def test_api_mapping(api_func, target_func, args):
    with mock.patch(target_func) as mocked_target_func:
        result = api_func(*args)
        if inspect.isgeneratorfunction(api_func):
            tuple(result)

    assert mocked_target_func.called
