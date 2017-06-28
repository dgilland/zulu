# -*- coding: utf-8 -*-

import mock
import pytest
import warnings

import zulu

from .fixtures import parametrize


@parametrize('api_func, target_func', [
    (zulu.now, 'zulu.zulu.Zulu.now'),
    (zulu.parse, 'zulu.zulu.Zulu.parse'),
    (zulu.range, 'zulu.zulu.Zulu.range'),
    (zulu.span_range, 'zulu.zulu.Zulu.span_range'),
    (zulu.parse_delta, 'zulu.delta.Delta.parse')
])
def test_api_mapping(api_func, target_func):
    with mock.patch(target_func) as mocked_target_func:
        api_func()

    assert mocked_target_func.called
