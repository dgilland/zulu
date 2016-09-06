# -*- coding: utf-8 -*-

from datetime import timedelta
import pickle

import pytest

from zulu import ParseError, Delta
from zulu._compat import PY2

from .fixtures import parametrize


@parametrize('obj,expected', [
    (timedelta(seconds=60), Delta(seconds=60)),
    (60, Delta(seconds=60)),
    ('32m', Delta(minutes=32)),
    ('2h32m', Delta(hours=2, minutes=32)),
    ('3d2h32m', Delta(days=3, hours=2, minutes=32)),
    ('1w3d2h32m', Delta(weeks=1, days=3, hours=2, minutes=32)),
    ('1w 3d 2h 32m', Delta(weeks=1, days=3, hours=2, minutes=32)),
    ('1 w 3 d 2 h 32 m', Delta(weeks=1, days=3, hours=2, minutes=32)),
    ('4:13', Delta(minutes=4, seconds=13)),
    ('4:13:02', Delta(hours=4, minutes=13, seconds=2)),
    ('4:13:02.266', Delta(hours=4,
                          minutes=13,
                          seconds=2,
                          microseconds=266000)),
    ('2:04:13:02.266', Delta(days=2,
                             hours=4,
                             minutes=13,
                             seconds=2,
                             microseconds=266000)),
    ('2 days, 4:13:02', Delta(days=2, hours=4, minutes=13, seconds=2)),
    ('2 days, 4:13:02.266', Delta(days=2,
                                  hours=4,
                                  minutes=13,
                                  seconds=2,
                                  microseconds=266000)),
    ('5hr34m56s', Delta(hours=5, minutes=34, seconds=56)),
    ('5 hours, 34 minutes, 56 seconds', Delta(hours=5,
                                              minutes=34,
                                              seconds=56)),
    ('5 hrs, 34 mins, 56 secs', Delta(hours=5, minutes=34, seconds=56)),
    ('2 days, 5 hours, 34 minutes, 56 seconds', Delta(days=2,
                                                      hours=5,
                                                      minutes=34,
                                                      seconds=56)),
    ('1.2 m', Delta(seconds=72)),
    ('1.2 min', Delta(seconds=72)),
    ('1.2 mins', Delta(seconds=72)),
    ('1.2 minute', Delta(seconds=72)),
    ('1.2 minutes', Delta(seconds=72)),
    ('172 hours', Delta(days=7, seconds=14400)),
    ('172 hr', Delta(days=7, seconds=14400)),
    ('172 h', Delta(days=7, seconds=14400)),
    ('172 hrs', Delta(days=7, seconds=14400)),
    ('172 hour', Delta(days=7, seconds=14400)),
    ('1.24 days', Delta(days=1, seconds=20736)),
    ('5 d', Delta(days=5)),
    ('5 day', Delta(days=5)),
    ('5 days', Delta(days=5)),
    ('5.6 wk', Delta(days=39, seconds=17280)),
    ('5.6 week', Delta(days=39, seconds=17280)),
    ('5.6 weeks', Delta(days=39, seconds=17280)),
])
def test_timedelta_parse(obj, expected):
    assert Delta.parse(obj) == expected


@parametrize('obj,exception', [
    ({}, TypeError),
    ('', ParseError),
    ('a', ParseError),
])
def test_timedelta_parse_invalid(obj, exception):
    with pytest.raises(exception):
        Delta.parse(obj)


@parametrize('delta,opts,expected', [
    (Delta(seconds=5), {}, '5 seconds'),
    (Delta(seconds=5), {'format': 'short'}, '5 sec'),
    (Delta(seconds=5), {'format': 'narrow'}, '5s'),
    (Delta(seconds=5), {'add_direction': True}, 'in 5 seconds'),
    (Delta(seconds=-5), {'add_direction': True}, '5 seconds ago'),
    (Delta(days=1, hours=10), {}, '1 day'),
    (Delta(days=1), {'granularity': 'year'}, '1 year'),
    (Delta(minutes=15), {'threshold': 0.15}, '0 hours'),
    (Delta(hours=23), {'threshold': 0.85}, '1 day'),
    (Delta(hours=23), {'threshold': 1.00}, '23 hours'),
    (Delta(hours=23), {'threshold': 1.00, 'locale': 'de'}, '23 Stunden'),
])
def test_timedelta_format(delta, opts, expected):
    assert delta.format(**opts) == expected


@parametrize('opts,exception', [
    ({'granularity': 'invalid'}, ValueError),
    ({'format': 'invalid'}, ValueError),
])
def test_timedelta_format_exception(opts, exception):
    with pytest.raises(exception):
        Delta(1).format(**opts)


def test_timedelta_math_operations_return_type():
    delta = Delta(days=1, hours=1, minutes=1, seconds=1, microseconds=1)

    assert isinstance(delta + delta, Delta)
    assert isinstance(delta - delta, Delta)
    assert isinstance(delta * 1, Delta)
    assert isinstance(delta / 1, Delta)
    assert isinstance(delta // 1, Delta)
    assert isinstance(abs(delta), Delta)
    assert isinstance(+delta, Delta)
    assert isinstance(-delta, Delta)

    if not PY2:
        assert isinstance(delta % delta, Delta)
        assert isinstance(divmod(delta, delta)[1], Delta)


def test_timedelta_pickle():
    delta = Delta(hours=1)
    assert pickle.loads(pickle.dumps(delta)) == delta
