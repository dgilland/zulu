# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta
from time import localtime, mktime, struct_time

from iso8601 import UTC
import pytest
import pytz
from tzlocal import get_localzone

from zulu import DateTime, ParseError
from zulu.parser import DATE_PATTERN_TO_DIRECTIVE


from .fixtures import parametrize


eastern = pytz.timezone('US/Eastern')


def test_new_defaults():
    assert DateTime() == DateTime.fromtimestamp(0)


@parametrize('factory', [
    DateTime.utcnow,
    datetime.utcnow
])
def test_now_is_utcnow(factory):
    dt = DateTime.now()
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
    (DateTime(2000, 1, 1),
     datetime(2000, 1, 1, tzinfo=UTC)),
])
def test_parse(string, expected):
    assert DateTime.parse(string) == expected


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
def test_parse_format(string, kargs, expected):
    assert DateTime.parse(string, **kargs) == expected


@parametrize('dt,pattern,expected', [
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'YYYY', '2000'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'YY', '00'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'MMMM', 'January'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'MMM', 'Jan'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'MM', '01'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'M', '1'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'DDD', '005'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'DD', '05'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'D', '5'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'dd', '05'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'd', '5'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'EEEE', 'Wednesday'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'EEE', 'Wed'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'EE', 'Wed'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'E', 'Wed'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'eee', 'Wed'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'ee', 'Wed'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'e', '3'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'HH', '13'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'H', '13'),
    (DateTime(2000, 1, 5, 9, 7, 8, 123456), 'HH', '09'),
    (DateTime(2000, 1, 5, 9, 7, 8, 123456), 'H', '9'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'hh', '01'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'h', '1'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'mm', '07'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'm', '7'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'ss', '08'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 's', '8'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'SSSSSS', '123456'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'SSSSS', '12345'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'SSSS', '1234'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'SSS', '123'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'SS', '12'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'S', '1'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'A', 'PM'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'a', 'pm'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'Z', '+0000'),
    (DateTime(2000, 1, 5, 13, 7, 8, 123456), 'ZZ', '+00:00'),
    (DateTime(1970, 1, 1, 0, 17, 30), 'X', '1050.0'),
    (DateTime(), ' ', ' '),
])
def test_format_pattern(dt, pattern, expected):
    assert dt.format(pattern) == expected


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
def test_parse_pattern_mapping(string, pattern):
    pat_dt = DateTime.parse(string, DATE_PATTERN_TO_DIRECTIVE[pattern])
    dt = DateTime.parse(string, pattern)

    assert pat_dt == dt


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
def test_parse_invalid(string, kargs, exception):
    with pytest.raises(exception):
        DateTime.parse(string, **kargs)


@parametrize('dt,expected', [
    (eastern.localize(datetime(2000, 1, 1)),
     datetime(2000, 1, 1, 5, tzinfo=pytz.UTC)),
    (DateTime(2000, 1, 1, tzinfo='UTC'),
     datetime(2000, 1, 1, tzinfo=pytz.UTC))
])
def test_fromdatetime(dt, expected):
    assert DateTime.fromdatetime(dt) == expected


@parametrize('factory,timestamp,expected', [
    (DateTime.fromtimestamp, 0, datetime(1970, 1, 1, tzinfo=pytz.UTC)),
    (DateTime.utcfromtimestamp, 0, datetime(1970, 1, 1, tzinfo=pytz.UTC)),
])
def test_fromtimestamp(factory, timestamp, expected):
    assert factory(timestamp) == expected


@parametrize('struct,expected', [
    (struct_time((2016, 7, 29, 21, 23, 50, 4, 211, 0)),
     DateTime(2016, 7, 29, 21, 23, 50))
])
def test_fromgmtime(struct, expected):
    assert DateTime.fromgmtime(struct) == expected


def test_fromordinal():
    assert DateTime.fromordinal(730120) == DateTime(2000, 1, 1)


def test_fromlocaltime():
    now = localtime()
    assert DateTime.fromlocaltime(now).timestamp() == mktime(now)


@parametrize('date,time,expected', [
    (datetime(2000, 1, 1), time(12, 30),
     DateTime(2000, 1, 1, 12, 30)),
    (date(2000, 1, 1), time(12, 30),
     DateTime(2000, 1, 1, 12, 30)),
    (DateTime(2000, 1, 1), DateTime(1990, 12, 3, 12, 30),
     DateTime(2000, 1, 1, 12, 30))
])
def test_combine(date, time, expected):
    dt = DateTime.combine(date, time)
    assert dt == expected


@parametrize('dt,properties', [
    (DateTime(2000, 1, 2, 3, 4, 5, 6),
     {'year': 2000,
      'month': 1,
      'day': 2,
      'hour': 3,
      'minute': 4,
      'second': 5,
      'microsecond': 6,
      'min': DateTime(1, 1, 1),
      'max': DateTime(9999, 12, 31, 23, 59, 59, 999999),
      'epoch': DateTime(1970, 1, 1),
      'resolution': timedelta(microseconds=1),
      'naive': datetime(2000, 1, 2, 3, 4, 5, 6),
      'datetime': datetime(2000, 1, 2, 3, 4, 5, 6, pytz.UTC)}),
])
def test_basic_properties(dt, properties):
    for prop, val in properties.items():
        assert getattr(dt, prop) == val

    assert type(dt.naive) is datetime
    assert type(dt.datetime) is datetime


@parametrize('dt,methods', [
    (DateTime(2000, 1, 2, 3, 4, 5, 6),
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
def test_basic_property_methods(dt, methods):
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
def test_isleap(year, expected):
    assert DateTime(year).isleap() == expected


@parametrize('dt,year_or_dt,expected', [
    (DateTime(1900), 2000, 24),
    (DateTime(2000), 1900, -24),
    (DateTime(1), DateTime(9999), 2424)
])
def test_leapdays(dt, year_or_dt, expected):
    assert dt.leapdays(year_or_dt) == expected


def test_copy():
    dt = DateTime(2000, 1, 1)
    copy = dt.copy()

    assert copy is not dt
    assert copy == dt


@parametrize('method,dt,delta,expected', [
    ('shift', DateTime(2000, 1, 1), {'days': 1}, DateTime(2000, 1, 2)),
    ('add', DateTime(2000, 1, 1), {'days': 1}, DateTime(2000, 1, 2)),
    ('sub', DateTime(2000, 1, 1), {'days': 1}, DateTime(1999, 12, 31)),
    ('shift', DateTime(2000, 1, 1), {'days': -1}, DateTime(1999, 12, 31)),
    ('add', DateTime(2000, 1, 1), {'days': -1}, DateTime(1999, 12, 31)),
    ('sub', DateTime(2000, 1, 1), {'days': -1}, DateTime(2000, 1, 2)),
    ('shift', DateTime(2000, 1, 1), {'years': 1}, DateTime(2001, 1, 1)),
    ('shift', DateTime(2000, 1, 1), {'years': -1}, DateTime(1999, 1, 1)),
    ('shift', DateTime(2000, 1, 1), {'weeks': 1}, DateTime(2000, 1, 8)),
    ('shift', DateTime(2000, 1, 1), {'weeks': -1}, DateTime(1999, 12, 25)),
    ('shift', DateTime(2000, 1, 1), {'months': 1}, DateTime(2000, 2, 1)),
    ('shift', DateTime(2000, 1, 1), {'months': -1}, DateTime(1999, 12, 1)),
    ('shift', DateTime(2000, 1, 1),
     {'years': 2, 'months': 7, 'weeks': 13, 'days': 400},
     DateTime(2003, 12, 5)),
])
def test_shift(method, dt, delta, expected):
    assert getattr(dt, method)(**delta) == expected


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


def test_str_format():
    dt = DateTime(2000, 1, 1)
    assert '{0}'.format(dt) == dt.isoformat()
    assert '{0:%Y-%m-%dT%H:%M:%S}'.format(dt) == dt.format('%Y-%m-%dT%H:%M:%S')


@parametrize('dt,fmt,expected', [
    (DateTime(2000, 1, 1, 12, 30),
     '%Y-%m-%dT%H:%M:%S%z',
     '2000-01-01T12:30:00+0000'),
    (DateTime(2000, 1, 1, 12, 30),
     '%a %b %d',
     'Sat Jan 01')
])
def test_strftime(dt, fmt, expected):
    assert dt.strftime(fmt) == expected


@parametrize('string,fmt,expected', [
    ('2000-01-01T12:30:00',
     '%Y-%m-%dT%H:%M:%S',
     DateTime(2000, 1, 1, 12, 30)),
])
def test_strptime(string, fmt, expected):
    assert DateTime.strptime(string, fmt) == expected


@parametrize('dt,args,expected', [
    (DateTime(2000, 1, 1, 12, 30, 45, 15),
     {},
     '2000-01-01T12:30:45.000015+00:00'),
    (DateTime(2000, 1, 1, 12, 30),
     {'tz': 'US/Eastern'},
     '2000-01-01T07:30:00-05:00'),
    (DateTime(2000, 1, 1, 12, 30),
     {'format': '%a %b %d'},
     'Sat Jan 01')
])
def test_format(dt, args, expected):
    assert dt.format(**args) == expected


def test_abc():
    import zulu
    dt = zulu.now()
    print(dt.microsecond)
    print(zulu.parser.format(dt, 'SSS'))


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
def test_astimezone(dt, tzinfo, expected):
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


@parametrize('dt,frame,expected', [
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'second',
     DateTime(2015, 2, 5, 12, 30, 15)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'minute',
     DateTime(2015, 2, 5, 12, 30)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'hour',
     DateTime(2015, 2, 5, 12)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'day',
     DateTime(2015, 2, 5)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'month',
     DateTime(2015, 2, 1)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'year',
     DateTime(2015, 1, 1)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'decade',
     DateTime(2010, 1, 1)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'century',
     DateTime(2000, 1, 1)),
])
def test_start_of_frame(dt, frame, expected):
    assert dt.start_of(frame) == expected


@parametrize('dt,frame,expected', [
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'second',
     DateTime(2015, 2, 5, 12, 30, 15, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'minute',
     DateTime(2015, 2, 5, 12, 30, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'hour',
     DateTime(2015, 2, 5, 12, 59, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'day',
     DateTime(2015, 2, 5, 23, 59, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'month',
     DateTime(2015, 2, 28, 23, 59, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'year',
     DateTime(2015, 12, 31, 23, 59, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'decade',
     DateTime(2019, 12, 31, 23, 59, 59, 999999)),
    (DateTime(2015, 2, 5, 12, 30, 15, 123456),
     'century',
     DateTime(2099, 12, 31, 23, 59, 59, 999999)),
])
def test_end_of_frame(dt, frame, expected):
    assert dt.end_of(frame) == expected


@parametrize('dt,span,count,expected', [
    (DateTime(2015, 4, 4, 12, 30),
     'century',
     1,
     (DateTime(2000, 1, 1, 0, 0),
      DateTime(2099, 12, 31, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'decade',
     1,
     (DateTime(2010, 1, 1, 0, 0),
      DateTime(2019, 12, 31, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'century',
     3,
     (DateTime(2000, 1, 1, 0, 0),
      DateTime(2299, 12, 31, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'decade',
     3,
     (DateTime(2010, 1, 1, 0, 0),
      DateTime(2039, 12, 31, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'year',
     1,
     (DateTime(2015, 1, 1, 0, 0),
      DateTime(2015, 12, 31, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'month',
     1,
     (DateTime(2015, 4, 1, 0, 0),
      DateTime(2015, 4, 30, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'day',
     3,
     (DateTime(2015, 4, 4, 0, 0),
      DateTime(2015, 4, 6, 23, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'hour',
     2,
     (DateTime(2015, 4, 4, 12, 0),
      DateTime(2015, 4, 4, 13, 59, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30),
     'minute',
     5,
     (DateTime(2015, 4, 4, 12, 30, 0),
      DateTime(2015, 4, 4, 12, 34, 59, 999999))),
    (DateTime(2015, 4, 4, 12, 30, 47),
     'second',
     20,
     (DateTime(2015, 4, 4, 12, 30, 47, 0),
      DateTime(2015, 4, 4, 12, 31, 6, 999999)))
])
def test_span(dt, span, count, expected):
    time_span_tuple = dt.span(span, count)
    assert time_span_tuple == expected


def test_span_attribute_error():
    frame = 'temp'
    dt = DateTime(2015, 4, 4, 12, 30)
    with pytest.raises(ValueError) as exc:
        dt.span(frame)

    assert 'The given time frame {0} is invalid'.format(frame) in str(exc)


@parametrize('frame,start,end,expected', [
    (
        'century',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2215, 4, 4, 12, 30),
        [(DateTime(2000, 1, 1, 0, 0),
          DateTime(2099, 12, 31, 23, 59, 59, 999999)),
         (DateTime(2100, 1, 1, 0, 0),
          DateTime(2199, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'decade',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2049, 4, 4, 12, 30),
        [(DateTime(2010, 1, 1, 0, 0),
          DateTime(2019, 12, 31, 23, 59, 59, 999999)),
         (DateTime(2020, 1, 1, 0, 0),
          DateTime(2029, 12, 31, 23, 59, 59, 999999)),
         (DateTime(2030, 1, 1, 0, 0),
          DateTime(2039, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'year',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2018, 4, 4, 12, 30),
        [(DateTime(2015, 1, 1, 0, 0),
          DateTime(2015, 12, 31, 23, 59, 59, 999999)),
         (DateTime(2016, 1, 1, 0, 0),
          DateTime(2016, 12, 31, 23, 59, 59, 999999)),
         (DateTime(2017, 1, 1, 0, 0),
          DateTime(2017, 12, 31, 23, 59, 59, 999999))]
    ),
    (
        'month',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 8, 4, 12, 30),
        [(DateTime(2015, 4, 1, 0, 0),
          DateTime(2015, 4, 30, 23, 59, 59, 999999)),
         (DateTime(2015, 5, 1, 0, 0),
          DateTime(2015, 5, 31, 23, 59, 59, 999999)),
         (DateTime(2015, 6, 1, 0, 0),
          DateTime(2015, 6, 30, 23, 59, 59, 999999)),
         (DateTime(2015, 7, 1, 0, 0),
          DateTime(2015, 7, 31, 23, 59, 59, 999999))]
    ),
    (
        'day',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 4, 8, 12, 30),
        [(DateTime(2015, 4, 4, 0, 0),
          DateTime(2015, 4, 4, 23, 59, 59, 999999)),
         (DateTime(2015, 4, 5, 0, 0),
          DateTime(2015, 4, 5, 23, 59, 59, 999999)),
         (DateTime(2015, 4, 6, 0, 0),
          DateTime(2015, 4, 6, 23, 59, 59, 999999)),
         (DateTime(2015, 4, 7, 0, 0),
          DateTime(2015, 4, 7, 23, 59, 59, 999999))]
    ),
    (
        'hour',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 4, 4, 16, 30),
        [(DateTime(2015, 4, 4, 12, 0),
          DateTime(2015, 4, 4, 12, 59, 59, 999999)),
         (DateTime(2015, 4, 4, 13, 0),
          DateTime(2015, 4, 4, 13, 59, 59, 999999)),
         (DateTime(2015, 4, 4, 14, 0),
          DateTime(2015, 4, 4, 14, 59, 59, 999999)),
         (DateTime(2015, 4, 4, 15, 0),
          DateTime(2015, 4, 4, 15, 59, 59, 999999))]
    ),
    (
        'minute',
        DateTime(2015, 4, 4, 12, 30, 0),
        DateTime(2015, 4, 4, 12, 34, 0),
        [(DateTime(2015, 4, 4, 12, 30, 0),
          DateTime(2015, 4, 4, 12, 30, 59, 999999)),
         (DateTime(2015, 4, 4, 12, 31, 0),
          DateTime(2015, 4, 4, 12, 31, 59, 999999)),
         (DateTime(2015, 4, 4, 12, 32, 0),
          DateTime(2015, 4, 4, 12, 32, 59, 999999)),
         (DateTime(2015, 4, 4, 12, 33, 0),
          DateTime(2015, 4, 4, 12, 33, 59, 999999))]
    ),
    (
        'second',
        DateTime(2015, 4, 4, 12, 30, 1),
        DateTime(2015, 4, 4, 12, 30, 5),
        [(DateTime(2015, 4, 4, 12, 30, 1, 0),
          DateTime(2015, 4, 4, 12, 30, 1, 999999)),
         (DateTime(2015, 4, 4, 12, 30, 2, 0),
          DateTime(2015, 4, 4, 12, 30, 2, 999999)),
         (DateTime(2015, 4, 4, 12, 30, 3, 0),
          DateTime(2015, 4, 4, 12, 30, 3, 999999)),
         (DateTime(2015, 4, 4, 12, 30, 4, 0),
          DateTime(2015, 4, 4, 12, 30, 4, 999999))]
    ),
])
def test_span_range(frame, start, end, expected):
    span_range = []
    for time_span in DateTime.span_range(frame, start, end):
        span_range.append(time_span)

    assert span_range == expected


@parametrize('frame,start,end,expected', [
    (
        'century',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2215, 4, 4, 12, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2115, 4, 4, 12, 30)]
    ),
    (
        'decade',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2045, 4, 4, 12, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2025, 4, 4, 12, 30),
         DateTime(2035, 4, 4, 12, 30)]
    ),
    (
        'year',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2018, 4, 4, 12, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2016, 4, 4, 12, 30),
         DateTime(2017, 4, 4, 12, 30)]
    ),
    (
        'month',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 7, 4, 12, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2015, 5, 4, 12, 30),
         DateTime(2015, 6, 4, 12, 30)]
    ),
    (
        'day',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 4, 7, 12, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2015, 4, 5, 12, 30),
         DateTime(2015, 4, 6, 12, 30)]
    ),
    (
        'hour',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 4, 4, 15, 30),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2015, 4, 4, 13, 30),
         DateTime(2015, 4, 4, 14, 30)]
    ),
    (
        'minute',
        DateTime(2015, 4, 4, 12, 30),
        DateTime(2015, 4, 4, 12, 33),
        [DateTime(2015, 4, 4, 12, 30),
         DateTime(2015, 4, 4, 12, 31),
         DateTime(2015, 4, 4, 12, 32)]
    ),
    (
        'second',
        DateTime(2015, 4, 4, 12, 30, 0),
        DateTime(2015, 4, 4, 12, 30, 3),
        [DateTime(2015, 4, 4, 12, 30, 0),
         DateTime(2015, 4, 4, 12, 30, 1),
         DateTime(2015, 4, 4, 12, 30, 2)]
    ),
])
def test_range(frame, start, end, expected):
    time_range = []
    for date_time in DateTime.range(frame, start, end):
        time_range.append(date_time)

    assert time_range == expected


@parametrize('frame,start,end,expected_error', [
    ('century',
     1,
     DateTime(2015, 4, 4, 12, 30, 0),
     'Provided value {0} is invalid datetime'.format(1)),
    ('year',
     DateTime(2015, 4, 4, 12, 30, 0),
     1,
     'Provided value {0} is invalid datetime'.format(1)),
    ('year',
     DateTime(2019, 4, 4, 12, 30, 0),
     DateTime(2015, 4, 4, 12, 30, 0),
     'Start datetime should always be less than end datetime')
])
def test_span_range_error(frame, start, end, expected_error):
    span_range = []
    with pytest.raises(ValueError) as exc:
        for time_span in DateTime.span_range(frame, start, end):
            span_range.append(time_span)

    assert len(span_range) == 0
    assert expected_error in str(exc)
