# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from iso8601 import UTC
import pytest
import pytz
from tzlocal import get_localzone

from zulu import DateTime, ParseError


from .fixtures import parametrize


eastern = pytz.timezone('US/Eastern')


@parametrize('string,expected', [
    ('2000',
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('2000-01',
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('2000-01-01',
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('2000-03-05',
     datetime(2000, 3, 5, tzinfo=UTC)),
    ('2000-01-01T12:30',
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC)),
    ('2000-01-01 12:30',
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC)),
    ('2000-01-01T12:30:30',
     datetime(2000, 1, 1, 12, 30, 30, tzinfo=UTC)),
    ('2000-01-01T12:30:30-0400',
     datetime(2000, 1, 1, 16, 30, 30, tzinfo=UTC)),
    ('2000-01-01T12:00:00-2359',
     datetime(2000, 1, 2, 11, 59, tzinfo=UTC)),
    ('2000-01-01T12:00:00+2359',
     datetime(1999, 12, 31, 12, 1, tzinfo=UTC)),
    (datetime(2000, 1, 1, tzinfo=UTC),
     datetime(2000, 1, 1, tzinfo=UTC)),
    (DateTime(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC)),
])
def test_parse(string, expected):
    assert DateTime.parse(string).datetime == expected


@parametrize('string,kargs,expected', [
    ('2000',
     {'formats': '%Y'},
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': '%m-%d-%Y %I:%M %p'},
     datetime(2000, 1, 5, 0, 30, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': '%m-%d-%Y %I:%M %p', 'default_tzinfo': eastern},
     datetime(2000, 1, 5, 5, 30, tzinfo=UTC)),
])
def test_parse_formats(string, kargs, expected):
    assert DateTime.parse(string, **kargs).datetime == expected


@parametrize('string', [
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
def test_parse_invalid(string):
    with pytest.raises(ParseError):
        DateTime.parse(string)


@parametrize('dt,expected', [
    (eastern.localize(datetime(2000, 1, 1)),
     datetime(2000, 1, 1, 5, tzinfo=pytz.UTC)),
    (DateTime(2000, 1, 1, tzinfo='UTC'),
     datetime(2000, 1, 1, tzinfo=pytz.UTC))
])
def test_fromdatetime(dt, expected):
    assert DateTime.fromdatetime(dt).datetime == expected


@parametrize('timestamp,expected', [
    (0, datetime(1970, 1, 1, tzinfo=pytz.UTC)),
])
def test_fromtimestamp(timestamp, expected):
    assert DateTime.fromtimestamp(timestamp).datetime == expected


@parametrize('dt,properties', [
    (DateTime(2000, 1, 2, 3, 4, 5, 6),
     {'year': 2000,
      'month': 1,
      'day': 2,
      'hour': 3,
      'minute': 4,
      'second': 5,
      'microsecond': 6,
      'naive': datetime(2000, 1, 2, 3, 4, 5, 6)}),
])
def test_basic_properties(dt, properties):
    for prop, val in properties.items():
        assert getattr(dt, prop) == val


def test_copy():
    dt = DateTime(2000, 1, 1)
    copy = dt.copy()

    assert copy is not dt
    assert copy.datetime == dt.datetime


@parametrize('dt,offset,expected', [
    (DateTime(2000, 1, 1), {'days': 1}, (2000, 1, 2)),
])
def test_offset(dt, offset, expected):
    assert dt.offset(**offset) == DateTime(*expected)


@parametrize('dt,replace,expected', [
    (DateTime(2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10},
     DateTime(1999, 12, 31, 12, 30, 15, 10)),
    (DateTime(2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10,
      'tzinfo': 'US/Eastern'},
     DateTime(1999, 12, 31, 17, 30, 15, 10)),
])
def test_replace(dt, replace, expected):
    assert dt.replace(**replace) == expected


def test_iter():
    dt = DateTime(2000, 1, 1)
    expected = (2000, 1, 1, 0, 0, 0, 0, pytz.UTC)

    assert tuple(dt) == expected
    assert list(dt) == list(expected)


@parametrize('dt,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15), '2000-01-01T12:30:45.000015+00:00'),
    (DateTime(2000, 1, 1, 12, 30, 45), '2000-01-01T12:30:45+00:00'),
    (DateTime(2000, 1, 1, 12), '2000-01-01T12:00:00+00:00'),
    (DateTime(2000, 1, 1), '2000-01-01T00:00:00+00:00'),
])
def test_isoformat(dt, expected):
    assert dt.isoformat() == expected


def test_str():
    dt = DateTime(2000, 1, 1)
    assert str(dt) == dt.isoformat()


@parametrize('dt,args,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     {},
     '2000-01-01T12:30:45.000015+00:00'),
    (DateTime(2000, 1, 1, 12, 30),
     {'tzinfo': 'US/Eastern'},
     '2000-01-01T07:30:00-05:00'),
    (DateTime(2000, 1, 1, 12, 30),
     {'format': '%a %b %d'},
     'Sat Jan 01')
])
def test_format(dt, args, expected):
    assert dt.format(**args) == expected


@parametrize('dt,tzinfo,expected', [
    (DateTime(2000, 1, 1, 10),
     None,
     datetime(2000, 1, 1, 10, tzinfo=pytz.UTC).astimezone(get_localzone())),
    (DateTime(2000, 1, 1, 10),
     'local',
     datetime(2000, 1, 1, 10, tzinfo=pytz.UTC).astimezone(get_localzone())),
    (DateTime(2000, 1, 1, 10),
     'US/Eastern',
     eastern.localize(datetime(2000, 1, 1, 5, 0))),
    (DateTime(2000, 1, 1, 10),
     pytz.timezone('US/Eastern'),
     eastern.localize(datetime(2000, 1, 1, 5, 0)))
])
def test_localize(dt, tzinfo, expected):
    ldt = dt.localize(tzinfo)

    assert ldt.year == expected.year
    assert ldt.month == expected.month
    assert ldt.day == expected.day
    assert ldt.hour == expected.hour
    assert ldt.minute == expected.minute
    assert ldt.second == expected.second
    assert ldt.microsecond == expected.microsecond
    assert ldt.tzinfo == expected.tzinfo


@parametrize('dt,delta,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1),
     DateTime(2000, 1, 2, 13, 31, 46, 1016)),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(weeks=1),
     DateTime(2000, 1, 8, 12, 30, 45, 15)),
])
def test_add(dt, delta, expected):
    dt += delta
    assert dt == expected


@parametrize('dt,offset,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1),
     DateTime(1999, 12, 31, 11, 29, 43, 999014)),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(1999, 12, 31, 11, 29, 43, 999014),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1)),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     datetime(1999, 12, 31, 11, 29, 43, 999014),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1)),
    (DateTime(1999, 12, 31, 11, 29, 43, 999014),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(days=-1,
               hours=-1,
               minutes=-1,
               seconds=-1,
               milliseconds=-1,
               microseconds=-1)),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(weeks=1),
     DateTime(1999, 12, 25, 12, 30, 45, 15)),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(1999, 12, 25, 12, 30, 45, 15),
     timedelta(weeks=1)),
    (DateTime(1999, 12, 25, 12, 30, 45, 15),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     timedelta(weeks=-1)),
])
def test_subtract(dt, offset, expected):
    result = dt - offset
    assert result == expected


def test_hash():
    dt = DateTime(2000, 1, 1)
    assert hash(dt) == hash(datetime(2000, 1, 1, tzinfo=UTC))


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1),
     DateTime(2000, 1, 1),
     True),
    (DateTime(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC),
     True),
    (DateTime(2000, 1, 2),
     DateTime(2000, 1, 1),
     False),
    (DateTime(2000, 1, 2),
     datetime(2000, 1, 1, tzinfo=UTC),
     False),
])
def test_compare_equal(dt, other, expected):
    assert (dt == other) is expected


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1),
     DateTime(2000, 1, 1),
     False),
    (DateTime(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC),
     False),
    (DateTime(2000, 1, 2),
     DateTime(2000, 1, 1),
     True),
    (DateTime(2000, 1, 2),
     datetime(2000, 1, 1, tzinfo=UTC),
     True),
])
def test_compare_not_equal(dt, other, expected):
    assert (dt != other) is expected


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(2000, 1, 1, 12, 30),
     False),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     False),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     True),
])
def test_compare_less_than(dt, other, expected):
    assert (dt < other) is expected


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(2000, 1, 1, 12, 30),
     False),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     False),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
])
def test_compare_less_than_equal(dt, other, expected):
    assert (dt <= other) is expected


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(2000, 1, 1, 12, 30),
     True),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     False),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     False),
])
def test_compare_greater_than(dt, other, expected):
    assert (dt > other) is expected


@parametrize('dt,other,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     DateTime(2000, 1, 1, 12, 30),
     True),
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30, 45, 15),
     False),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     False),
    (DateTime(2000, 1, 1, 12, 30),
     DateTime(2000, 1, 1, 12, 30),
     True),
    (DateTime(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
])
def test_compare_greater_than_equal(dt, other, expected):
    assert (dt >= other) is expected
