# -*- coding: utf-8 -*-

import pytest

from zulu import TimeDelta

from .fixtures import parametrize


@parametrize('delta,opts,expected', [
    (TimeDelta(seconds=5), {}, '5 seconds'),
    (TimeDelta(seconds=5), {'style': 'short'}, '5 sec'),
    (TimeDelta(seconds=5), {'style': 'narrow'}, '5s'),
    (TimeDelta(seconds=5), {'add_direction': True}, 'in 5 seconds'),
    (TimeDelta(seconds=-5), {'add_direction': True}, '5 seconds ago'),
    (TimeDelta(days=1, hours=10), {}, '1 day'),
    (TimeDelta(days=1), {'granularity': 'year'}, '1 year'),
    (TimeDelta(minutes=15), {'threshold': 0.15}, '0 hours'),
    (TimeDelta(hours=23), {'threshold': 0.85}, '1 day'),
    (TimeDelta(hours=23), {'threshold': 1.00}, '23 hours'),
    (TimeDelta(hours=23), {'threshold': 1.00, 'locale': 'de'}, '23 Stunden'),
])
def test_format(delta, opts, expected):
    assert delta.format(**opts) == expected
