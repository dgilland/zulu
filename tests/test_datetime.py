# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta
import pickle
from time import localtime, mktime, struct_time

from dateutil.relativedelta import relativedelta
from iso8601 import UTC
import pytest
import pytz
from tzlocal import get_localzone

from zulu import Zulu, Delta, ParseError, create
from zulu.parser import DATE_PATTERN_TO_DIRECTIVE


from .fixtures import parametrize


eastern = pytz.timezone('US/Eastern')


def test_datetime_defaults():
    assert Zulu() == Zulu.fromtimestamp(0)
    assert create() == Zulu()


@parametrize('factory', [
    Zulu.utcnow,
    datetime.utcnow
])
def test_datetime_now_is_utcnow(factory):
    dt = Zulu.now()
    expected = factory()

    # NOTE: Intentionally skip comparison to microsecond since they will almost
    # always be different.
    assert dt.year == expected.year
    assert dt.month == expected.month
    assert dt.day == expected.day
    assert dt.hour == expected.hour
    assert dt.minute == expected.minute
    assert dt.second == expected.second


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
    (0,
     datetime(1970, 1, 1, tzinfo=UTC)),
    (datetime(2000, 1, 1, tzinfo=UTC),
     datetime(2000, 1, 1, tzinfo=UTC)),
    (Zulu(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC)),
])
def test_datetime_parse(string, expected):
    assert Zulu.parse(string) == expected


@parametrize('string,kargs,exception', [
    ('2000/01/01', {}, ParseError),
    ('01/01/2000', {}, ParseError),
    ('01-01-2000', {}, ParseError),
    ('2000-01-01X00:00:00', {}, ParseError),
    ('2000-01-01T00,00,00', {}, ParseError),
    ('2000-01-01T00:00:00+2400', {}, ParseError),
    ('2000-01-01T00:00:00-2400', {}, ParseError),
    ('2000-01-01T00:00:00+2500', {}, ParseError),
    ('2000-01-01T00:00:00-2500', {}, ParseError),
    ('2000-01-01T00:00:00', {'default_tz': 'invalid'}, ValueError),
])
def test_datetime_parse_invalid(string, kargs, exception):
    with pytest.raises(exception):
        Zulu.parse(string, **kargs)


@parametrize('string,kargs,expected', [
    ('2000',
     {'formats': '%Y'},
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('2000',
     {'formats': 'YYYY'},
     datetime(2000, 1, 1, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': '%m-%d-%Y %I:%M %p'},
     datetime(2000, 1, 5, 0, 30, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': 'M-d-YYYY h:m a'},
     datetime(2000, 1, 5, 0, 30, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': '%m-%d-%Y %I:%M %p', 'default_tz': eastern},
     datetime(2000, 1, 5, 5, 30, tzinfo=UTC)),
    ('1-5-2000 12:30 AM',
     {'formats': 'M-d-YYYY h:m a', 'default_tz': eastern},
     datetime(2000, 1, 5, 5, 30, tzinfo=UTC)),
    (('2016 16 July Jul 07 209 27 Wednesday Wed 3 '
      '04 4 34 22 479776 AM'),
     {'formats': ('%Y %y %B %b %m %j %d %A %a %w '
                  '%H %I %M %S %f %p')},
     datetime(2016, 7, 27, 4, 34, 22, 479776, tzinfo=UTC)),
    (('2016 16 July Jul 07 209 27 Wednesday Wed 3 '
      '04 4 34 22 479776 AM'),
     {'formats': ('YYYY YY MMMM MMM MM DDD dd EEEE EEE e '
                  'HH hh mm ss SSSSSS a')},
     datetime(2016, 7, 27, 4, 34, 22, 479776, tzinfo=UTC)),
])
def test_datetime_parse_format(string, kargs, expected):
    assert Zulu.parse(string, **kargs) == expected


@parametrize('dt,opts,expected', [
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'YYYY', '2000'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'YY', '00'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'MMMM', 'January'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456),
     {'format': 'MMMM', 'locale': 'fr'},
     'janvier'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'MMM', 'Jan'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456),
     {'format': 'MMM', 'locale': 'fr'},
     'janv.'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'MM', '01'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'M', '1'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'DDD', '005'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'DD', '05'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'D', '5'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'dd', '05'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'd', '5'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'EEEE', 'Wednesday'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456),
     {'format': 'EEEE', 'locale': 'fr'},
     'mercredi'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'EEE', 'Wed'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456),
     {'format': 'EEE', 'locale': 'fr'},
     'mer.'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'EE', 'Wed'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'E', 'Wed'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'eee', 'Wed'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'ee', '04'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'e', '4'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'HH', '13'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'H', '13'),
    (Zulu(2000, 1, 5, 9, 7, 8, 123456), 'HH', '09'),
    (Zulu(2000, 1, 5, 9, 7, 8, 123456), 'H', '9'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'hh', '01'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'h', '1'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'mm', '07'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'm', '7'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'ss', '08'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 's', '8'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'SSSSSS', '123456'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'SSSSS', '12346'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'SSSS', '1235'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'SSS', '123'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'SS', '12'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'S', '1'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'a', 'PM'),
    (Zulu(2000, 1, 5, 13, 7, 8, 123456), 'Z', '+0000'),
    (Zulu(), ' ', ' '),
])
def test_datetime_format_pattern(dt, opts, expected):
    if not isinstance(opts, dict):
        opts = {'format': opts}
    assert dt.format(**opts) == expected


@parametrize('string,pattern', [
    ('2000', 'YYYY'),
    ('00', 'YY'),
    ('January', 'MMMM'),
    ('Jan', 'MMM'),
    ('01', 'MM'),
    ('1', 'M'),
    ('207', 'DDD'),
    ('207', 'D'),
    ('05', 'dd'),
    ('5', 'd'),
    ('Monday', 'EEEE'),
    ('Mon', 'EEE'),
    ('Mon', 'EE'),
    ('Mon', 'E'),
    ('Mon', 'eee'),
    ('1', 'e'),
    ('13', 'HH'),
    ('3', 'H'),
    ('12', 'hh'),
    ('3', 'h'),
    ('07', 'mm'),
    ('59', 'mm'),
    ('07', 'ss'),
    ('59', 'ss'),
    ('000006', 'SSSSSS'),
    ('000006', 'SSSSS'),
    ('000006', 'SSSS'),
    ('000006', 'SS'),
    ('000006', 'S'),
    ('AM', 'a'),
])
def test_datetime_parse_pattern_mapping(string, pattern):
    pat_dt = Zulu.parse(string, DATE_PATTERN_TO_DIRECTIVE[pattern])
    dt = Zulu.parse(string, pattern)

    assert pat_dt == dt


@parametrize('dt,args,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     {},
     '2000-01-01T12:30:45.000015+00:00'),
    (Zulu(2000, 1, 1, 12, 30),
     {'tz': 'US/Eastern'},
     '2000-01-01T07:30:00-05:00'),
    (Zulu(2000, 1, 1, 12, 30),
     {'format': '%a %b %d'},
     'Sat Jan 01')
])
def test_datetime_format(dt, args, expected):
    assert dt.format(**args) == expected


@parametrize('dt,fmt,expected', [
    (Zulu(2000, 1, 1, 12, 30),
     '%Y-%m-%dT%H:%M:%S%z',
     '2000-01-01T12:30:00+0000'),
    (Zulu(2000, 1, 1, 12, 30),
     '%a %b %d',
     'Sat Jan 01')
])
def test_datetime_strftime(dt, fmt, expected):
    assert dt.strftime(fmt) == expected


@parametrize('string,fmt,expected', [
    ('2000-01-01T12:30:00',
     '%Y-%m-%dT%H:%M:%S',
     Zulu(2000, 1, 1, 12, 30)),
])
def test_datetime_strptime(string, fmt, expected):
    assert Zulu.strptime(string, fmt) == expected


@parametrize('dt,expected', [
    (eastern.localize(datetime(2000, 1, 1)),
     datetime(2000, 1, 1, 5, tzinfo=pytz.UTC)),
    (Zulu(2000, 1, 1, tzinfo='UTC'),
     datetime(2000, 1, 1, tzinfo=pytz.UTC))
])
def test_datetime_fromdatetime(dt, expected):
    assert Zulu.fromdatetime(dt) == expected


@parametrize('factory,timestamp,expected', [
    (Zulu.fromtimestamp, 0, datetime(1970, 1, 1, tzinfo=pytz.UTC)),
    (Zulu.utcfromtimestamp, 0, datetime(1970, 1, 1, tzinfo=pytz.UTC)),
])
def test_datetime_fromtimestamp(factory, timestamp, expected):
    assert factory(timestamp) == expected


@parametrize('struct,expected', [
    (struct_time((2016, 7, 29, 21, 23, 50, 4, 211, 0)),
     Zulu(2016, 7, 29, 21, 23, 50))
])
def test_datetime_fromgmtime(struct, expected):
    assert Zulu.fromgmtime(struct) == expected


def test_datetime_fromordinal():
    assert Zulu.fromordinal(730120) == Zulu(2000, 1, 1)


def test_datetime_fromlocaltime():
    now = localtime()
    assert Zulu.fromlocaltime(now).timestamp() == mktime(now)


@parametrize('date,time,expected', [
    (datetime(2000, 1, 1), time(12, 30),
     Zulu(2000, 1, 1, 12, 30)),
    (date(2000, 1, 1), time(12, 30),
     Zulu(2000, 1, 1, 12, 30)),
    (Zulu(2000, 1, 1), Zulu(1990, 12, 3, 12, 30),
     Zulu(2000, 1, 1, 12, 30))
])
def test_datetime_combine(date, time, expected):
    dt = Zulu.combine(date, time)
    assert dt == expected


@parametrize('dt,properties', [
    (Zulu(2000, 1, 2, 3, 4, 5, 6),
     {'year': 2000,
      'month': 1,
      'day': 2,
      'hour': 3,
      'minute': 4,
      'second': 5,
      'microsecond': 6,
      'min': Zulu(1, 1, 1),
      'max': Zulu(9999, 12, 31, 23, 59, 59, 999999),
      'epoch': Zulu(1970, 1, 1),
      'resolution': timedelta(microseconds=1),
      'naive': datetime(2000, 1, 2, 3, 4, 5, 6),
      'datetime': datetime(2000, 1, 2, 3, 4, 5, 6, pytz.UTC)}),
])
def test_datetime_basic_properties(dt, properties):
    for prop, val in properties.items():
        assert getattr(dt, prop) == val

    assert type(dt.naive) is datetime
    assert type(dt.datetime) is datetime


@parametrize('dt,methods', [
    (Zulu(2000, 1, 2, 3, 4, 5, 6),
     {'utcoffset': timedelta(0),
      'tzname': 'UTC',
      'dst': timedelta(0),
      'date': date(2000, 1, 2),
      'time': time(3, 4, 5, 6),
      'timetz': time(3, 4, 5, 6, tzinfo=UTC),
      'weekday': 6,
      'isoweekday': 7,
      'isocalendar': (1999, 52, 7),
      'ctime': 'Sun Jan  2 03:04:05 2000',
      'toordinal': 730121,
      'timetuple': struct_time((2000, 1, 2, 3, 4, 5, 6, 2, 0)),
      'utctimetuple': struct_time((2000, 1, 2, 3, 4, 5, 6, 2, 0)),
      'timestamp': 946782245.000006}),
])
def test_datetime_basic_property_methods(dt, methods):
    for meth, val in methods.items():
        assert getattr(dt, meth)() == val


@parametrize('year,expected', [
    (100, False),
    (104, True),
    (1900, False),
    (1904, True),
    (2000, True),
    (2001, False),
    (2004, True),
])
def test_datetime_is_leap_year(year, expected):
    assert Zulu(year).is_leap_year() == expected


@parametrize('dt,expected', [
    (Zulu(2001, 1, 1), 31),
    (Zulu(2001, 2, 1), 28),
    (Zulu(2001, 3, 1), 31),
    (Zulu(2001, 4, 1), 30),
    (Zulu(2001, 5, 1), 31),
    (Zulu(2001, 6, 1), 30),
    (Zulu(2001, 7, 1), 31),
    (Zulu(2001, 8, 1), 31),
    (Zulu(2001, 9, 1), 30),
    (Zulu(2001, 10, 1), 31),
    (Zulu(2001, 11, 1), 30),
    (Zulu(2001, 12, 1), 31),
    (Zulu(2004, 2, 1), 29),
])
def test_datetime_days_in_month(dt, expected):
    assert dt.days_in_month() == expected


def test_datetime_copy():
    dt = Zulu(2000, 1, 1)
    copy = dt.copy()

    assert copy is not dt
    assert copy == dt


@parametrize('dt,replace,expected', [
    (Zulu(2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10},
     Zulu(1999, 12, 31, 12, 30, 15, 10)),
    (Zulu(2000, 1, 1),
     {'year': 1999,
      'month': 12,
      'day': 31,
      'hour': 12,
      'minute': 30,
      'second': 15,
      'microsecond': 10,
      'tzinfo': 'US/Eastern'},
     Zulu(1999, 12, 31, 17, 30, 15, 10)),
])
def test_datetime_replace(dt, replace, expected):
    assert dt.replace(**replace) == expected


def test_datetime_as_iter():
    dt = Zulu(2000, 1, 1)
    expected = (2000, 1, 1, 0, 0, 0, 0, pytz.UTC)

    assert tuple(dt) == expected
    assert list(dt) == list(expected)


@parametrize('dt,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15), '2000-01-01T12:30:45.000015+00:00'),
    (Zulu(2000, 1, 1, 12, 30, 45), '2000-01-01T12:30:45+00:00'),
    (Zulu(2000, 1, 1, 12), '2000-01-01T12:00:00+00:00'),
    (Zulu(2000, 1, 1), '2000-01-01T00:00:00+00:00'),
])
def test_datetime_isoformat(dt, expected):
    assert dt.isoformat() == expected


def test_datetime_as_string():
    dt = Zulu(2000, 1, 1)
    assert str(dt) == dt.isoformat()


def test_datetime_string_format():
    dt = Zulu(2000, 1, 1)
    assert '{0}'.format(dt) == dt.isoformat()
    assert '{0:%Y-%m-%dT%H:%M:%S}'.format(dt) == dt.format('%Y-%m-%dT%H:%M:%S')


@parametrize('dt,tzinfo,expected', [
    (Zulu(2000, 1, 1, 10),
     None,
     datetime(2000, 1, 1, 10, tzinfo=pytz.UTC).astimezone(get_localzone())),
    (Zulu(2000, 1, 1, 10),
     'local',
     datetime(2000, 1, 1, 10, tzinfo=pytz.UTC).astimezone(get_localzone())),
    (Zulu(2000, 1, 1, 10),
     'US/Eastern',
     eastern.localize(datetime(2000, 1, 1, 5, 0))),
    (Zulu(2000, 1, 1, 10),
     pytz.timezone('US/Eastern'),
     eastern.localize(datetime(2000, 1, 1, 5, 0)))
])
def test_datetime_astimezone(dt, tzinfo, expected):
    ldt = dt.astimezone(tzinfo)

    assert type(ldt) is datetime
    assert ldt.year == expected.year
    assert ldt.month == expected.month
    assert ldt.day == expected.day
    assert ldt.hour == expected.hour
    assert ldt.minute == expected.minute
    assert ldt.second == expected.second
    assert ldt.microsecond == expected.microsecond
    assert ldt.tzinfo == expected.tzinfo


@parametrize('method,dt,delta,expected', [
    ('shift',
     Zulu(2000, 1, 1),
     {'days': 1},
     Zulu(2000, 1, 2)),
    ('shift',
     Zulu(2000, 1, 1),
     timedelta(days=1),
     Zulu(2000, 1, 2)),
    ('shift',
     Zulu(2000, 1, 1),
     timedelta(days=-1),
     Zulu(1999, 12, 31)),
    ('shift',
     Zulu(2000, 1, 1),
     relativedelta(days=1),
     Zulu(2000, 1, 2)),
    ('add',
     Zulu(2000, 1, 1),
     {'days': 1},
     Zulu(2000, 1, 2)),
    ('add',
     Zulu(2000, 1, 1),
     timedelta(days=1),
     Zulu(2000, 1, 2)),
    ('add',
     Zulu(2000, 1, 1),
     relativedelta(days=1),
     Zulu(2000, 1, 2)),
    ('subtract',
     Zulu(2000, 1, 1),
     {'days': 1},
     Zulu(1999, 12, 31)),
    ('subtract',
     Zulu(2000, 1, 1),
     timedelta(days=1),
     Zulu(1999, 12, 31)),
    ('subtract',
     Zulu(2000, 1, 1),
     relativedelta(days=1),
     Zulu(1999, 12, 31)),
    ('subtract',
     Zulu(2000, 1, 1),
     Delta(days=1),
     Zulu(1999, 12, 31)),
    ('subtract',
     Zulu(2000, 1, 1),
     Zulu(1999, 12, 31),
     Delta(days=1)),
    ('subtract',
     Zulu(1999, 12, 31),
     Zulu(2000, 1, 1),
     Delta(days=-1)),
    ('subtract',
     Zulu(2000, 1, 1),
     datetime(1999, 12, 31),
     Delta(days=1)),
    ('shift',
     Zulu(2000, 1, 1),
     {'days': -1},
     Zulu(1999, 12, 31)),
    ('add',
     Zulu(2000, 1, 1),
     {'days': -1},
     Zulu(1999, 12, 31)),
    ('subtract',
     Zulu(2000, 1, 1),
     {'days': -1},
     Zulu(2000, 1, 2)),
    ('shift',
     Zulu(2000, 1, 1),
     {'years': 1},
     Zulu(2001, 1, 1)),
    ('shift',
     Zulu(2000, 1, 1),
     {'years': -1},
     Zulu(1999, 1, 1)),
    ('shift',
     Zulu(2000, 1, 1),
     {'weeks': 1},
     Zulu(2000, 1, 8)),
    ('shift',
     Zulu(2000, 1, 1),
     {'weeks': -1},
     Zulu(1999, 12, 25)),
    ('shift',
     Zulu(2000, 1, 1),
     {'months': 1},
     Zulu(2000, 2, 1)),
    ('shift',
     Zulu(2000, 1, 1),
     {'months': -1},
     Zulu(1999, 12, 1)),
    ('shift',
     Zulu(2000, 1, 1),
     {'years': 2, 'months': 7, 'weeks': 13, 'days': 400},
     Zulu(2003, 12, 5)),
])
def test_datetime_shift(method, dt, delta, expected):
    meth = getattr(dt, method)

    if isinstance(delta, dict):
        result = meth(**delta)
    else:
        result = meth(delta)

    assert result == expected
    assert type(result) == type(expected)


@parametrize('dt,delta,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1),
     Zulu(2000, 1, 2, 13, 31, 46, 1016)),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     timedelta(weeks=1),
     Zulu(2000, 1, 8, 12, 30, 45, 15)),
    (Zulu(2000, 1, 1, 12, 30, 45, 0),
     60.123456,
     Zulu(2000, 1, 1, 12, 31, 45, 123456)),
])
def test_datetime_addition(dt, delta, expected):
    dt1 = (dt + delta)
    dt2 = (delta + dt)

    assert dt1 == dt2 == expected
    assert type(dt1) == type(dt2) == Zulu


def test_datetime_addition_invalid_type():
    with pytest.raises(TypeError):
        Zulu() + 'string'


@parametrize('dt,offset,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     timedelta(days=1,
               hours=1,
               minutes=1,
               seconds=1,
               milliseconds=1,
               microseconds=1),
     Zulu(1999, 12, 31, 11, 29, 43, 999014)),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(1999, 12, 31, 11, 29, 43, 999014),
     Delta(days=1,
           hours=1,
           minutes=1,
           seconds=1,
           milliseconds=1,
           microseconds=1)),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     datetime(1999, 12, 31, 11, 29, 43, 999014),
     Delta(days=1,
           hours=1,
           minutes=1,
           seconds=1,
           milliseconds=1,
           microseconds=1)),
    (Zulu(1999, 12, 31, 11, 29, 43, 999014),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     Delta(days=-1,
           hours=-1,
           minutes=-1,
           seconds=-1,
           milliseconds=-1,
           microseconds=-1)),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     timedelta(weeks=1),
     Zulu(1999, 12, 25, 12, 30, 45, 15)),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(1999, 12, 25, 12, 30, 45, 15),
     Delta(weeks=1)),
    (Zulu(1999, 12, 25, 12, 30, 45, 15),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     Delta(weeks=-1)),
])
def test_datetime_subtraction(dt, offset, expected):
    result = dt - offset
    assert result == expected
    assert type(result) == type(expected)


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1), Zulu(2000, 1, 2), 'in 1 day'),
    (Zulu(2000, 1, 2), Zulu(2000, 1, 1), '1 day ago'),
    (Zulu(2000, 1, 1, 0), Zulu(2000, 1, 1, 1), 'in 1 hour'),
    (Zulu(2000, 1, 1, 1), Zulu(2000, 1, 1, 0), '1 hour ago'),
    (Zulu(2000, 1, 1, 0), Zulu(2000, 1, 1, 2), 'in 2 hours'),
    (Zulu(2000, 1, 1, 2), Zulu(2000, 1, 1, 0), '2 hours ago'),
    (Zulu(2000, 1, 1, 0, 0), Zulu(2000, 1, 1, 0, 1), 'in 1 minute'),
    (Zulu(2000, 1, 1, 0, 1), Zulu(2000, 1, 1, 0, 0), '1 minute ago'),
    (Zulu(2000, 1, 1, 0, 0, 0),
     Zulu(2000, 1, 1, 0, 0, 1),
     'in 1 second'),
    (Zulu(2000, 1, 1, 0, 0, 1),
     Zulu(2000, 1, 1, 0, 0, 0),
     '1 second ago'),
    (Zulu(2000, 1, 1, 0, 0, 0, 0),
     Zulu(2000, 1, 1, 0, 0, 0, 1),
     'in 0 seconds'),
    (Zulu(2000, 1, 1, 0, 0, 0, 1),
     Zulu(2000, 1, 1, 0, 0, 0, 0),
     '1 second ago'),
])
def test_datetime_time_to(dt, other, expected):
    assert dt.time_to(other) == expected


def test_datetime_time_to_now():
    assert Zulu.now().shift(minutes=1).time_to_now() == '1 minute ago'
    assert Zulu.now().shift(minutes=-1).time_to_now() == 'in 1 minute'


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1), Zulu(2000, 1, 2), '1 day ago'),
    (Zulu(2000, 1, 2), Zulu(2000, 1, 1), 'in 1 day'),
    (Zulu(2000, 1, 1, 0), Zulu(2000, 1, 1, 1), '1 hour ago'),
    (Zulu(2000, 1, 1, 1), Zulu(2000, 1, 1, 0), 'in 1 hour'),
    (Zulu(2000, 1, 1, 0), Zulu(2000, 1, 1, 2), '2 hours ago'),
    (Zulu(2000, 1, 1, 2), Zulu(2000, 1, 1, 0), 'in 2 hours'),
    (Zulu(2000, 1, 1, 0, 0), Zulu(2000, 1, 1, 0, 1), '1 minute ago'),
    (Zulu(2000, 1, 1, 0, 1), Zulu(2000, 1, 1, 0, 0), 'in 1 minute'),
    (Zulu(2000, 1, 1, 0, 0, 0),
     Zulu(2000, 1, 1, 0, 0, 1),
     '1 second ago'),
    (Zulu(2000, 1, 1, 0, 0, 1),
     Zulu(2000, 1, 1, 0, 0, 0),
     'in 1 second'),
    (Zulu(2000, 1, 1, 0, 0, 0, 0),
     Zulu(2000, 1, 1, 0, 0, 0, 1),
     '1 second ago'),
    (Zulu(2000, 1, 1, 0, 0, 0, 1),
     Zulu(2000, 1, 1, 0, 0, 0, 0),
     'in 0 seconds'),
])
def test_datetime_time_from(dt, other, expected):
    assert dt.time_from(other) == expected


def test_datetime_time_from_now():
    assert Zulu.now().shift(minutes=1).time_from_now() == 'in 1 minute'
    assert Zulu.now().shift(minutes=-1).time_from_now() == '1 minute ago'


def test_datetime_hash():
    dt = Zulu(2000, 1, 1)
    assert hash(dt) == hash(datetime(2000, 1, 1, tzinfo=UTC))


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1),
     Zulu(2000, 1, 1),
     True),
    (Zulu(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC),
     True),
    (Zulu(2000, 1, 2),
     Zulu(2000, 1, 1),
     False),
    (Zulu(2000, 1, 2),
     datetime(2000, 1, 1, tzinfo=UTC),
     False),
])
def test_datetime_compare_equal(dt, other, expected):
    assert (dt == other) is expected


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1),
     Zulu(2000, 1, 1),
     False),
    (Zulu(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC),
     False),
    (Zulu(2000, 1, 2),
     Zulu(2000, 1, 1),
     True),
    (Zulu(2000, 1, 2),
     datetime(2000, 1, 1, tzinfo=UTC),
     True),
])
def test_datetime_compare_not_equal(dt, other, expected):
    assert (dt != other) is expected


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(2000, 1, 1, 12, 30),
     False),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     False),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     True),
])
def test_datetime_compare_less_than(dt, other, expected):
    assert (dt < other) is expected


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(2000, 1, 1, 12, 30),
     False),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     False),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
])
def test_datetime_compare_less_than_equal(dt, other, expected):
    assert (dt <= other) is expected


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(2000, 1, 1, 12, 30),
     True),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     False),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     False),
])
def test_datetime_compare_greater_than(dt, other, expected):
    assert (dt > other) is expected


@parametrize('dt,other,expected', [
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     Zulu(2000, 1, 1, 12, 30),
     True),
    (Zulu(2000, 1, 1, 12, 30, 45, 15),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30, 45, 15),
     False),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, 45, 15, tzinfo=UTC),
     False),
    (Zulu(2000, 1, 1, 12, 30),
     Zulu(2000, 1, 1, 12, 30),
     True),
    (Zulu(2000, 1, 1, 12, 30),
     datetime(2000, 1, 1, 12, 30, tzinfo=UTC),
     True),
])
def test_datetime_compare_greater_than_equal(dt, other, expected):
    assert (dt >= other) is expected


@parametrize('dt,frame,expected', [
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'second',
     Zulu(2015, 2, 5, 12, 30, 15)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'minute',
     Zulu(2015, 2, 5, 12, 30)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'hour',
     Zulu(2015, 2, 5, 12)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'day',
     Zulu(2015, 2, 5)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'month',
     Zulu(2015, 2, 1)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'year',
     Zulu(2015, 1, 1)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'decade',
     Zulu(2010, 1, 1)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'century',
     Zulu(2000, 1, 1)),
])
def test_datetime_start_of_frame(dt, frame, expected):
    assert dt.start_of(frame) == expected


@parametrize('dt,frame,expected', [
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'second',
     Zulu(2015, 2, 5, 12, 30, 15, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'minute',
     Zulu(2015, 2, 5, 12, 30, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'hour',
     Zulu(2015, 2, 5, 12, 59, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'day',
     Zulu(2015, 2, 5, 23, 59, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'month',
     Zulu(2015, 2, 28, 23, 59, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'year',
     Zulu(2015, 12, 31, 23, 59, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'decade',
     Zulu(2019, 12, 31, 23, 59, 59, 999999)),
    (Zulu(2015, 2, 5, 12, 30, 15, 123456),
     'century',
     Zulu(2099, 12, 31, 23, 59, 59, 999999)),
])
def test_datetime_end_of_frame(dt, frame, expected):
    assert dt.end_of(frame) == expected


@parametrize('dt,span,count,expected', [
    (Zulu(2015, 4, 4, 12, 30),
     'century',
     1,
     (Zulu(2000, 1, 1, 0, 0),
      Zulu(2099, 12, 31, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'decade',
     1,
     (Zulu(2010, 1, 1, 0, 0),
      Zulu(2019, 12, 31, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'century',
     3,
     (Zulu(2000, 1, 1, 0, 0),
      Zulu(2299, 12, 31, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'decade',
     3,
     (Zulu(2010, 1, 1, 0, 0),
      Zulu(2039, 12, 31, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'year',
     1,
     (Zulu(2015, 1, 1, 0, 0),
      Zulu(2015, 12, 31, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'month',
     1,
     (Zulu(2015, 4, 1, 0, 0),
      Zulu(2015, 4, 30, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'day',
     3,
     (Zulu(2015, 4, 4, 0, 0),
      Zulu(2015, 4, 6, 23, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'hour',
     2,
     (Zulu(2015, 4, 4, 12, 0),
      Zulu(2015, 4, 4, 13, 59, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30),
     'minute',
     5,
     (Zulu(2015, 4, 4, 12, 30, 0),
      Zulu(2015, 4, 4, 12, 34, 59, 999999))),
    (Zulu(2015, 4, 4, 12, 30, 47),
     'second',
     20,
     (Zulu(2015, 4, 4, 12, 30, 47, 0),
      Zulu(2015, 4, 4, 12, 31, 6, 999999)))
])
def test_datetime_span(dt, span, count, expected):
    time_span_tuple = dt.span(span, count)
    assert time_span_tuple == expected


def test_datetime_span_frame_error():
    frame = 'temp'
    dt = Zulu(2015, 4, 4, 12, 30)

    with pytest.raises(ValueError) as exc:
        dt.span(frame)

    assert 'Time frame must be one of' in str(exc.value)
    assert "not '{0}'".format(frame)


@parametrize('frame,start,end,expected', [
    (
        'century',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2215, 4, 4, 12, 30),
        [(Zulu(2000, 1, 1, 0, 0),
          Zulu(2099, 12, 31, 23, 59, 59, 999999)),
         (Zulu(2100, 1, 1, 0, 0),
          Zulu(2199, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'decade',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2049, 4, 4, 12, 30),
        [(Zulu(2010, 1, 1, 0, 0),
          Zulu(2019, 12, 31, 23, 59, 59, 999999)),
         (Zulu(2020, 1, 1, 0, 0),
          Zulu(2029, 12, 31, 23, 59, 59, 999999)),
         (Zulu(2030, 1, 1, 0, 0),
          Zulu(2039, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'year',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2018, 4, 4, 12, 30),
        [(Zulu(2015, 1, 1, 0, 0),
          Zulu(2015, 12, 31, 23, 59, 59, 999999)),
         (Zulu(2016, 1, 1, 0, 0),
          Zulu(2016, 12, 31, 23, 59, 59, 999999)),
         (Zulu(2017, 1, 1, 0, 0),
          Zulu(2017, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'month',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 8, 4, 12, 30),
        [(Zulu(2015, 4, 1, 0, 0),
          Zulu(2015, 4, 30, 23, 59, 59, 999999)),
         (Zulu(2015, 5, 1, 0, 0),
          Zulu(2015, 5, 31, 23, 59, 59, 999999)),
         (Zulu(2015, 6, 1, 0, 0),
          Zulu(2015, 6, 30, 23, 59, 59, 999999)),
         (Zulu(2015, 7, 1, 0, 0),
          Zulu(2015, 7, 31, 23, 59, 59, 999999))]
    ),
    (
        'day',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 4, 8, 12, 30),
        [(Zulu(2015, 4, 4, 0, 0),
          Zulu(2015, 4, 4, 23, 59, 59, 999999)),
         (Zulu(2015, 4, 5, 0, 0),
          Zulu(2015, 4, 5, 23, 59, 59, 999999)),
         (Zulu(2015, 4, 6, 0, 0),
          Zulu(2015, 4, 6, 23, 59, 59, 999999)),
         (Zulu(2015, 4, 7, 0, 0),
          Zulu(2015, 4, 7, 23, 59, 59, 999999))]
    ),
    (
        'hour',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 4, 4, 16, 30),
        [(Zulu(2015, 4, 4, 12, 0),
          Zulu(2015, 4, 4, 12, 59, 59, 999999)),
         (Zulu(2015, 4, 4, 13, 0),
          Zulu(2015, 4, 4, 13, 59, 59, 999999)),
         (Zulu(2015, 4, 4, 14, 0),
          Zulu(2015, 4, 4, 14, 59, 59, 999999)),
         (Zulu(2015, 4, 4, 15, 0),
          Zulu(2015, 4, 4, 15, 59, 59, 999999))]
    ),
    (
        'minute',
        Zulu(2015, 4, 4, 12, 30, 0),
        Zulu(2015, 4, 4, 12, 34, 0),
        [(Zulu(2015, 4, 4, 12, 30, 0),
          Zulu(2015, 4, 4, 12, 30, 59, 999999)),
         (Zulu(2015, 4, 4, 12, 31, 0),
          Zulu(2015, 4, 4, 12, 31, 59, 999999)),
         (Zulu(2015, 4, 4, 12, 32, 0),
          Zulu(2015, 4, 4, 12, 32, 59, 999999)),
         (Zulu(2015, 4, 4, 12, 33, 0),
          Zulu(2015, 4, 4, 12, 33, 59, 999999))]
    ),
    (
        'second',
        Zulu(2015, 4, 4, 12, 30, 1),
        Zulu(2015, 4, 4, 12, 30, 5),
        [(Zulu(2015, 4, 4, 12, 30, 1, 0),
          Zulu(2015, 4, 4, 12, 30, 1, 999999)),
         (Zulu(2015, 4, 4, 12, 30, 2, 0),
          Zulu(2015, 4, 4, 12, 30, 2, 999999)),
         (Zulu(2015, 4, 4, 12, 30, 3, 0),
          Zulu(2015, 4, 4, 12, 30, 3, 999999)),
         (Zulu(2015, 4, 4, 12, 30, 4, 0),
          Zulu(2015, 4, 4, 12, 30, 4, 999999))]
    ),
    (
        'second',
        Zulu(2015, 4, 4, 12, 30, 5),
        Zulu(2015, 4, 4, 12, 30, 1),
        []
    ),
])
def test_datetime_span_range(frame, start, end, expected):
    span_range = []
    for time_span in Zulu.span_range(frame, start, end):
        span_range.append(time_span)

    assert span_range == expected


@parametrize('frame,start,end', [
    ('century', '1', Zulu(2015, 4, 4, 12, 30, 0)),
    ('year', Zulu(2015, 4, 4, 12, 30, 0), '1')
])
def test_datetime_span_range_error(frame, start, end):
    with pytest.raises(ParseError):
        list(Zulu.span_range(frame, start, end))


@parametrize('frame,start,end,expected', [
    (
        'century',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2215, 4, 4, 12, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2115, 4, 4, 12, 30)]
    ),
    (
        'decade',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2045, 4, 4, 12, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2025, 4, 4, 12, 30),
         Zulu(2035, 4, 4, 12, 30)]
    ),
    (
        'year',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2018, 4, 4, 12, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2016, 4, 4, 12, 30),
         Zulu(2017, 4, 4, 12, 30)]
    ),
    (
        'month',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 7, 4, 12, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2015, 5, 4, 12, 30),
         Zulu(2015, 6, 4, 12, 30)]
    ),
    (
        'day',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 4, 7, 12, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2015, 4, 5, 12, 30),
         Zulu(2015, 4, 6, 12, 30)]
    ),
    (
        'hour',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 4, 4, 15, 30),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2015, 4, 4, 13, 30),
         Zulu(2015, 4, 4, 14, 30)]
    ),
    (
        'hour',
        Zulu(2015, 4, 4, 12, 30, 15, 123456),
        Zulu(2015, 4, 4, 15, 30),
        [Zulu(2015, 4, 4, 12, 30, 15, 123456),
         Zulu(2015, 4, 4, 13, 30, 15, 123456)]
    ),
    (
        'minute',
        Zulu(2015, 4, 4, 12, 30),
        Zulu(2015, 4, 4, 12, 33),
        [Zulu(2015, 4, 4, 12, 30),
         Zulu(2015, 4, 4, 12, 31),
         Zulu(2015, 4, 4, 12, 32)]
    ),
    (
        'second',
        Zulu(2015, 4, 4, 12, 30, 0),
        Zulu(2015, 4, 4, 12, 30, 3),
        [Zulu(2015, 4, 4, 12, 30, 0),
         Zulu(2015, 4, 4, 12, 30, 1),
         Zulu(2015, 4, 4, 12, 30, 2)]
    ),
    (
        'second',
        Zulu(2015, 4, 4, 12, 30, 3),
        Zulu(2015, 4, 4, 12, 30, 0),
        []
    ),
])
def test_datetime_range(frame, start, end, expected):
    time_range = list(Zulu.range(frame, start, end))

    assert time_range == expected


@parametrize('frame,start,end', [
    ('century', '1', Zulu(2015, 4, 4, 12, 30, 0)),
    ('year', Zulu(2015, 4, 4, 12, 30, 0), '1')
])
def test_datetime_range_error(frame, start, end):
    with pytest.raises(ParseError):
        list(Zulu.range(frame, start, end))


def test_datetime_pickle():
    dt = Zulu()
    assert pickle.loads(pickle.dumps(dt)) == dt
