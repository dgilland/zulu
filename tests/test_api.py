# -*- coding: utf-8 -*-

import mock
import pytest
import warnings

import zulu

from .fixtures import parametrize


@parametrize('api_func, target_func', [
    (zulu.now, 'zulu.datetime.Zulu.now'),
    (zulu.parse, 'zulu.datetime.Zulu.parse'),
    (zulu.range, 'zulu.datetime.Zulu.range'),
    (zulu.span_range, 'zulu.datetime.Zulu.span_range'),
    (zulu.parse_delta, 'zulu.timedelta.Delta.parse')
])
def test_api_mapping(api_func, target_func):
    with mock.patch(target_func) as mocked_target_func:
        api_func()

    assert mocked_target_func.called


@parametrize('api_func,args', [
    (zulu.delta, [0])
])
def test_api_deprecated(api_func, args):
    pytest.deprecated_call(api_func, *args)
