# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
import pytz
from tzlocal import get_localzone

from zulu import DateTime, ParseError


from .fixtures import parametrize


eastern = pytz.timezone('US/Eastern')


@parametrize('text,expected', [
    ('2000', datetime(2000, 1, 1, tzinfo=pytz.UTC)),
    ('2000-01', datetime(2000, 1, 1, tzinfo=pytz.UTC)),
    ('2000-01-01', datetime(2000, 1, 1, tzinfo=pytz.UTC)),
    ('2000-03-05', datetime(2000, 3, 5, tzinfo=pytz.UTC)),
    ('2000-01-01T12:30', datetime(2000, 1, 1, 12, 30, tzinfo=pytz.UTC)),
    ('2000-01-01 12:30', datetime(2000, 1, 1, 12, 30, tzinfo=pytz.UTC)),
    ('2000-01-01T12:30:30', datetime(2000, 1, 1, 12, 30, 30, tzinfo=pytz.UTC)),
    ('2000-01-01T12:30:30-0400',
     datetime(2000, 1, 1, 16, 30, 30, tzinfo=pytz.UTC)),
    ('2000-01-01T12:00:00-2359',
     datetime(2000, 1, 2, 11, 59, tzinfo=pytz.UTC)),
    ('2000-01-01T12:00:00+2359',
     datetime(1999, 12, 31, 12, 1, tzinfo=pytz.UTC)),
    (datetime(2000, 1, 1, tzinfo=pytz.UTC),
     datetime(2000, 1, 1, tzinfo=pytz.UTC))
])
def test_parse(text, expected):
    assert DateTime.parse(text).datetime == expected


@parametrize('text', [
    '2000/01/01',
    '01/01/2000',
    '01-01-2000',
    '2000-01-01X00:00:00',
    '2000-01-01T00,00,00',
    '2000-01-01T00:00:00+2400',
    '2000-01-01T00:00:00-2400',
    '2000-01-01T00:00:00+2500',
    '2000-01-01T00:00:00-2500',
])
def test_parse_invalid(text):
    with pytest.raises(ParseError):
        DateTime.parse(text)


@parametrize('args,properties', [
    ((2000, 1, 2, 3, 4, 5, 6), {'year': 2000,
                                'month': 1,
                                'day': 2,
                                'hour': 3,
                                'minute': 4,
                                'second': 5,
                                'microsecond': 6,
                                'naive': datetime(2000, 1, 2, 3, 4, 5, 6)}),
])
def test_basic_properties(args, properties):
    dt = DateTime(*args)

    for prop, val in properties.items():
        assert getattr(dt, prop) == val


def test_copy():
    dt = DateTime(2000, 1, 1)
    copy = dt.copy()

    assert copy is not dt
    assert copy.datetime == dt.datetime


@parametrize('struct,offset,expected', [
    ((2000, 1, 1), {'days': 1}, (2000, 1, 2)),
])
def test_offset(struct, offset, expected):
    dt = DateTime(*struct)
    assert dt.offset(**offset) == DateTime(*expected)


@parametrize('struct,replace,expected', [
    ((2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10,
      'tzinfo': 'utc'},
     (1999, 12, 31, 12, 30, 15, 10, 'utc')),
])
def test_replace(struct, replace, expected):
    dt = DateTime(*struct)
    assert dt.replace(**replace) == DateTime(*expected)


def test_iter():
    dt = DateTime(2000, 1, 1)
    expected = (2000, 1, 1, 0, 0, 0, 0, pytz.UTC)

    assert tuple(dt) == expected
    assert list(dt) == list(expected)


@parametrize('struct,expected', [
    ((2000, 1, 1, 12, 30, 45, 15), '2000-01-01T12:30:45.000015+00:00'),
    ((2000, 1, 1, 12, 30, 45), '2000-01-01T12:30:45+00:00'),
    ((2000, 1, 1, 12), '2000-01-01T12:00:00+00:00'),
    ((2000, 1, 1), '2000-01-01T00:00:00+00:00'),
])
def test_isoformat(struct, expected):
    dt = DateTime(*struct)
    assert dt.isoformat() == expected


@parametrize('struct,args,expected', [
    ((2000, 1, 1, 12, 30, 45, 15),
     {},
     '2000-01-01T12:30:45.000015+00:00'),
    ((2000, 1, 1, 12, 30),
     {'tzinfo': 'US/Eastern'},
     '2000-01-01T07:30:00-05:00'),
])
def test_format(struct, args, expected):
    dt = DateTime(*struct)
    assert dt.format(**args) == expected


@parametrize('struct,tzinfo,expected', [
    ((2000, 1, 1, 10), None,
     datetime(2000, 1, 1, 10, tzinfo=pytz.UTC).astimezone(get_localzone())),
    ((2000, 1, 1, 10), 'US/Eastern',
     eastern.localize(datetime(2000, 1, 1, 5, 0)))
])
def test_localize(struct, tzinfo, expected):
    dt = DateTime(*struct)
    dt = dt.localize(tzinfo)

    assert dt.year == expected.year
    assert dt.month == expected.month
    assert dt.day == expected.day
    assert dt.hour == expected.hour
    assert dt.minute == expected.minute
    assert dt.second == expected.second
    assert dt.microsecond == expected.microsecond
    assert dt.tzinfo == expected.tzinfo
