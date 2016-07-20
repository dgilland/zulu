# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
import pytz

from zulu import DateTime, ParseError


from .fixtures import parametrize


@parametrize('text,expected', [
    ('2000', datetime(2000, 1, 1, tzinfo=pytz.utc)),
    ('2000-01', datetime(2000, 1, 1, tzinfo=pytz.utc)),
    ('2000-01-01', datetime(2000, 1, 1, tzinfo=pytz.utc)),
    ('2000-03-05', datetime(2000, 3, 5, tzinfo=pytz.utc)),
    ('2000-01-01T12:30', datetime(2000, 1, 1, 12, 30, tzinfo=pytz.utc)),
    ('2000-01-01 12:30', datetime(2000, 1, 1, 12, 30, tzinfo=pytz.utc)),
    ('2000-01-01T12:30:30', datetime(2000, 1, 1, 12, 30, 30, tzinfo=pytz.utc)),
    ('2000-01-01T12:30:30-0400',
     datetime(2000, 1, 1, 16, 30, 30, tzinfo=pytz.utc)),
    ('2000-01-01T12:00:00-2359',
     datetime(2000, 1, 2, 11, 59, tzinfo=pytz.utc)),
    ('2000-01-01T12:00:00+2359',
     datetime(1999, 12, 31, 12, 1, tzinfo=pytz.utc)),
    (datetime(2000, 1, 1, tzinfo=pytz.utc),
     datetime(2000, 1, 1, tzinfo=pytz.utc))
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
                                'microsecond': 6}),
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


@parametrize('dt,replace,expected', [
    (DateTime(2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10,
      'tzinfo': 'utc'},
     DateTime(1999, 12, 31, 12, 30, 15, 10, 'utc')),
])
def test_replace(dt, replace, expected):
    assert dt.replace(**replace) == expected


def test_iter():
    dt = DateTime(2000, 1, 1)
    expected = (2000, 1, 1, 0, 0, 0, 0, pytz.utc)

    assert tuple(dt) == expected
    assert list(dt) == list(expected)
