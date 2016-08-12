# -*- coding: utf-8 -*-

from datetime import timedelta

import pytest

from zulu import ParseError, TimeDelta

from .fixtures import parametrize


@parametrize('obj,expected', [
    (timedelta(seconds=60), TimeDelta(seconds=60)),
    ('32m', TimeDelta(minutes=32)),
    ('2h32m', TimeDelta(hours=2, minutes=32)),
    ('3d2h32m', TimeDelta(days=3, hours=2, minutes=32)),
    ('1w3d2h32m', TimeDelta(weeks=1, days=3, hours=2, minutes=32)),
    ('1w 3d 2h 32m', TimeDelta(weeks=1, days=3, hours=2, minutes=32)),
    ('1 w 3 d 2 h 32 m', TimeDelta(weeks=1, days=3, hours=2, minutes=32)),
    ('4:13', TimeDelta(minutes=4, seconds=13)),
    ('4:13:02', TimeDelta(hours=4, minutes=13, seconds=2)),
    ('4:13:02.266', TimeDelta(hours=4,
                              minutes=13,
                              seconds=2,
                              microseconds=266000)),
    ('2:04:13:02.266', TimeDelta(days=2,
                                 hours=4,
                                 minutes=13,
                                 seconds=2,
                                 microseconds=266000)),
    ('2 days, 4:13:02', TimeDelta(days=2, hours=4, minutes=13, seconds=2)),
    ('2 days, 4:13:02.266', TimeDelta(days=2,
                                      hours=4,
                                      minutes=13,
                                      seconds=2,
                                      microseconds=266000)),
    ('5hr34m56s', TimeDelta(hours=5, minutes=34, seconds=56)),
    ('5 hours, 34 minutes, 56 seconds', TimeDelta(hours=5,
                                                  minutes=34,
                                                  seconds=56)),
    ('5 hrs, 34 mins, 56 secs', TimeDelta(hours=5, minutes=34, seconds=56)),
    ('2 days, 5 hours, 34 minutes, 56 seconds', TimeDelta(days=2,
                                                          hours=5,
                                                          minutes=34,
                                                          seconds=56)),
    ('1.2 m', TimeDelta(seconds=72)),
    ('1.2 min', TimeDelta(seconds=72)),
    ('1.2 mins', TimeDelta(seconds=72)),
    ('1.2 minute', TimeDelta(seconds=72)),
    ('1.2 minutes', TimeDelta(seconds=72)),
    ('172 hours', TimeDelta(days=7, seconds=14400)),
    ('172 hr', TimeDelta(days=7, seconds=14400)),
    ('172 h', TimeDelta(days=7, seconds=14400)),
    ('172 hrs', TimeDelta(days=7, seconds=14400)),
    ('172 hour', TimeDelta(days=7, seconds=14400)),
    ('1.24 days', TimeDelta(days=1, seconds=20736)),
    ('5 d', TimeDelta(days=5)),
    ('5 day', TimeDelta(days=5)),
    ('5 days', TimeDelta(days=5)),
    ('5.6 wk', TimeDelta(days=39, seconds=17280)),
    ('5.6 week', TimeDelta(days=39, seconds=17280)),
    ('5.6 weeks', TimeDelta(days=39, seconds=17280)),
])
def test_timedelta_parse(obj, expected):
    assert TimeDelta.parse(obj) == expected


@parametrize('obj,exception', [
    ({}, TypeError),
    ('', ParseError),
    ('a', ParseError),
])
def test_timedelta_parse_invalid(obj, exception):
    with pytest.raises(exception):
        TimeDelta.parse(obj)


@parametrize('delta,opts,expected', [
    (TimeDelta(seconds=5), {}, '5 seconds'),
    (TimeDelta(seconds=5), {'format': 'short'}, '5 sec'),
    (TimeDelta(seconds=5), {'format': 'narrow'}, '5s'),
    (TimeDelta(seconds=5), {'add_direction': True}, 'in 5 seconds'),
    (TimeDelta(seconds=-5), {'add_direction': True}, '5 seconds ago'),
    (TimeDelta(days=1, hours=10), {}, '1 day'),
    (TimeDelta(days=1), {'granularity': 'year'}, '1 year'),
    (TimeDelta(minutes=15), {'threshold': 0.15}, '0 hours'),
    (TimeDelta(hours=23), {'threshold': 0.85}, '1 day'),
    (TimeDelta(hours=23), {'threshold': 1.00}, '23 hours'),
    (TimeDelta(hours=23), {'threshold': 1.00, 'locale': 'de'}, '23 Stunden'),
])
def test_timedelta_format(delta, opts, expected):
    assert delta.format(**opts) == expected
