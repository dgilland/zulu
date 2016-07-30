# -*- coding: utf-8 -*-
"""The datetime module.
"""

from __future__ import absolute_import

import calendar
from datetime import datetime, timedelta
from functools import wraps
import time

from dateutil.relativedelta import relativedelta
import pytz
import tzlocal

from .parser import get_timezone, parse, _pattern_to_directive_formatting
from ._compat import string_types


class DateTime(datetime):
    """The DateTime class represents an immutable UTC datetime object. Any
    timezone information given to it during instantiation results in the
    datetime object being converted from that timezone to UTC. If timezone
    information is not given, then it's assumed the datetime is a UTC value.
    All arthimetic is perform on the underlying UTC datetime object. DateTime
    has no concept of timezone shifting in this regard. Instead, localization
    occurs only when formatting a DateTime object as a string.

    The DateTime class is a drop-in replacement for a native datetime object,
    but does not represent itself in any time zone other than UTC.

    Args:
        year (int): Date year ``1 <= year <= 9999``.
        month (int): Date month ``1 <= month <= 12``.
        day (int): Date day ``1 <= day <= number of days in the given month
            and year``
        hour (int, optional): Time hour ``0 <= hour < 24``. Defaults to ``0``.
        minute (int, optional): Time minute ``0 <= minute < 60``. Defaults to
            ``0``.
        second (int, optional): Time second ``0 <= second < 60``. Defaults to
            ``0``.
        microsecond (int, optional): Time microsecond ``0 <= microsecond <
            1000000``. Defaults to ``0``.
        tzinfo (None|str|tzinfo, optional): Timezone information as either a
            ``str`` or ``tzinfo`` subclass. If value is a ``str``, it will be
            converted to a ``pytz.timezone``. If value is ``None``, the
            datetime values given are assumed to in UTC. Defaults to ``None``.
    """
    def __new__(cls,
                year=1970,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
                tzinfo=None):
        if tzinfo and isinstance(tzinfo, string_types):
            tzinfo = pytz.timezone(tzinfo)

        naive = datetime(year, month, day, hour, minute, second, microsecond)

        if hasattr(tzinfo, 'localize'):
            dt = tzinfo.localize(naive, is_dst=None)
        elif tzinfo:
            dt = naive.replace(tzinfo=tzinfo)
        else:
            dt = pytz.UTC.localize(naive, is_dst=None)

        dt = dt.astimezone(pytz.UTC)

        return datetime.__new__(cls,
                                dt.year,
                                dt.month,
                                dt.day,
                                dt.hour,
                                dt.minute,
                                dt.second,
                                dt.microsecond,
                                dt.tzinfo)

    @classmethod
    def now(cls):
        """Return the current UTC date and time as :class:`.DateTime` object.

        Returns:
            :class:`.DateTime`
        """
        return cls.utcnow()

    @classmethod
    def parse(cls, obj, formats=None, default_tz=None):
        """Return :class:`.DateTime` object parsed from `obj`.

        Args:
            obj (mixed): Object to parse into a :class:`.DateTime` object.
            formats (list, optional): List of string formats to use when
                parsing. Defaults to ``['ISO8601', 'timestamp']``.
            default_tz (None|str|tzinfo, optional): Default timezone to use
                when parsed datetime object does not contain a timezone.
                Defaults to ``UTC``.

        Returns:
            :class:`.DateTime`
        """
        dt = parse(obj, formats=formats, default_tz=default_tz)
        return cls.fromdatetime(dt)

    @classmethod
    def fromdatetime(cls, dt):
        """Return :class:`.DateTime` object from a native datetime
        object.

        Returns:
            :class:`.DateTime`
        """
        return cls(dt.year,
                   dt.month,
                   dt.day,
                   dt.hour,
                   dt.minute,
                   dt.second,
                   dt.microsecond,
                   dt.tzinfo)

    @classmethod
    def fromtimestamp(cls, timestamp, tz=pytz.UTC):
        """Return :class:`.DateTime` object from a POSIX timestamp.

        Args:
            timestamp (int): POSIX timestamp such as is returned by
                ``time.time()``.
            tz (UTC): This argument is ignored and always set to UTC. It is
                present only for datetime class compatibility.

        Returns:
            :class:`.DateTime`
        """
        tz = pytz.UTC
        return super(DateTime, cls).fromtimestamp(timestamp, tz)

    @classmethod
    def utcfromtimestamp(cls, timestamp):
        """Return :class:`.DateTime` object from a POSIX timestamp.

        Args:
            timestamp (int): POSIX timestamp such as is returned by
                ``time.time()``.

        Returns:
            :class:`.DateTime`
        """
        return cls.fromtimestamp(timestamp)

    @classmethod
    def fromordinal(cls, ordinal):
        """Return :class:`.DateTime` object from a proleptic Gregorian ordinal,
        where January 1 of year 1 has ordinal 1.

        Args:
            ordinal (int): A proleptic Gregorian ordinal.

        Returns:
            :class:`.DateTime`
        """
        return cls.fromdatetime(datetime.fromordinal(ordinal))

    @classmethod
    def fromgmtime(cls, struct):
        """Return :class:`.DateTime` object from a ``tuple`` like that returned
        by ``time.gmtime`` that represents a UTC datetime.

        Args:
            struct (tuple): Tuple like that returned by ``time.gmtime``.

        Returns:
            :class:`.DateTime`
        """
        return cls.fromtimestamp(calendar.timegm(struct))

    @classmethod
    def fromlocaltime(cls, struct):
        """Return :class:`.DateTime` object from a ``tuple`` like that returned
        by ``time.localtime`` that represents a local datetime.

        Args:
            struct (tuple): Tuple like that returned by ``time.localtime``.

        Returns:
            :class:`.DateTime`
        """
        return cls.fromtimestamp(time.mktime(struct))

    @classmethod
    def combine(cls, date, time):
        """Return :class:`.DateTime` object by combining the date part from
        `date` and the time part from `time`.

        Args:
            date (mixed): Either a :class:`.DateTime`, ``datetime.date``,
                or ``datetime.datetime`` object to use as the date part.
            date (mixed): Either a :class:`.DateTime` or ``datetime.time``
                object to use as the time part.

        Returns:
            :class:`.DateTime`
        """
        if callable(getattr(date, 'date', None)):
            date = date.date()

        if callable(getattr(time, 'time', None)):
            time = time.time()

        return cls.fromdatetime(datetime.combine(date, time))

    @property
    def naive(self):
        """The datetime object as a naive datetime (tzinfo=None).

        .. note:: This returns a native datetime object.

        Returns:
            :class:`.DateTime`
        """
        return self.datetime.replace(tzinfo=None)

    @property
    def datetime(self):
        """The DateTime object as a native datetime.

        .. note:: This returns a native datetime object.

        Returns:
            :class:`datetime`
        """
        return datetime(*tuple(self))

    def timestamp(self):
        """Return the POSIX timestamp.

        Returns:
            :class:`float`
        """
        return (self - self.epoch).total_seconds()

    def copy(self):
        """Return a new :class`DateTime` instance with the same datetime value.

        Returns:
            :class:`.DateTime`
        """
        return DateTime(*tuple(self))

    def isleap(self):
        """Return whether this datetime's :attr:`year` is a leap year.

        Returns:
            bool
        """
        return calendar.isleap(self.year)

    def leapdays(self, year_or_dt):
        """Return the number of leap days between this datetime's :attr:`year`
        and `to_year`.

        Args:
            year_or_dt (int|datetime): Year or year from datetime to calculate
                leap days between.

        Returns:
            int
        """
        other_year = getattr(year_or_dt, 'year', year_or_dt)
        return calendar.leapdays(self.year, other_year)

    def format(self, format=None, tz=None):
        """Return datetime as a string using the format string `format` while
        optionally converting to timezone `tz` first.

        Args:
            format (str): Format to return string in. If ``None``, ISO 8601
                format is used. Defaults to ``None``.
            tz (None|str|tzinfo, optional): Timezone to convert to before
                formatting. Defaults to ``None``.

        Returns:
            :class:`str`
        """
        if tz is not None:
            dt = self.astimezone(tz)
        else:
            dt = self

        if format is None:
            return dt.isoformat()
        else:
            if '%' not in format:
                format = _pattern_to_directive_formatting(format)

            return dt.strftime(format)

    def astimezone(self, tz='local'):
        """Return datetime shifted to timezone `tz`.

        .. note:: This returns a native datetime object.

        Args:
            tz (None|str|tzinfo, optional): Timezone to shift to.

        Returns:
            :class:`.DateTime`
        """
        if tz is None:
            tz = 'local'
        tz = get_timezone(tz)
        return super(DateTime, self).astimezone(tz)

    def shift(self,
              years=0,
              months=0,
              weeks=0,
              days=0,
              hours=0,
              minutes=0,
              seconds=0,
              microseconds=0):
        """Shift datetime forward or backward using a timedelta created from
        the supplied arguments and return a new :class:`.DateTime` instance.

        Returns:
            :class:`.DateTime`
        """
        dt = self + relativedelta(years=years,
                                  months=months,
                                  weeks=weeks,
                                  days=days,
                                  hours=hours,
                                  minutes=minutes,
                                  seconds=seconds,
                                  microseconds=microseconds)

        return self.fromdatetime(dt)

    def add(self,
            years=0,
            months=0,
            weeks=0,
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            microseconds=0):
        """Add time using a timedelta created from the supplied arguments and
        return a new :class:`.DateTime` instance.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(years,
                          months,
                          weeks,
                          days,
                          hours,
                          minutes,
                          seconds,
                          microseconds)

    def sub(self,
            years=0,
            months=0,
            weeks=0,
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            microseconds=0):
        """Subtract time using a timedelta created from the supplied arguments
        and return a new :class:`.DateTime` instance.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(-years,
                          -months,
                          -weeks,
                          -days,
                          -hours,
                          -minutes,
                          -seconds,
                          -microseconds)

    def replace(self,
                year=None,
                month=None,
                day=None,
                hour=None,
                minute=None,
                second=None,
                microsecond=None,
                tzinfo=None):
        """Replace datetime attributes and return a new
        :class:`.DateTime` instance.

        Returns:
            :class:`.DateTime`
        """
        args = list(self)

        if year is not None:
            args[0] = year

        if month is not None:
            args[1] = month

        if day is not None:
            args[2] = day

        if hour is not None:
            args[3] = hour

        if minute is not None:
            args[4] = minute

        if second is not None:
            args[5] = second

        if microsecond is not None:
            args[6] = microsecond

        if tzinfo is not None:
            args[7] = tzinfo

        return DateTime(*args)

    def start_of_century(self):
        """Return a new :class:`.DateTime` set to the start of the century of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(years=-(self.year % 100),
                          months=-self.month + 1,
                          days=-self.day + 1,
                          hours=-self.hour,
                          minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_decade(self):
        """Return a new :class:`.DateTime` set to the start of the decade of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(years=-(self.year % 10),
                          months=-self.month + 1,
                          days=-self.day + 1,
                          hours=-self.hour,
                          minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_year(self):
        """Return a new :class:`.DateTime` set to the start of the year of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(months=-self.month + 1,
                          days=-self.day + 1,
                          hours=-self.hour,
                          minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_month(self):
        """Return a new :class:`.DateTime` set to the start of the month of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(days=-self.day + 1,
                          hours=-self.hour,
                          minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_day(self):
        """Return a new :class:`.DateTime` set to the start of the day of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(hours=-self.hour,
                          minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_hour(self):
        """Return a new :class:`.DateTime` set to the start of the hour of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(minutes=-self.minute,
                          seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_minute(self):
        """Return a new :class:`.DateTime` set to the start of the minute of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(seconds=-self.second,
                          microseconds=-self.microsecond)

    def start_of_second(self):
        """Return a new :class:`.DateTime` set to the start of the second of
        this datetime.

        Returns:
            :class:`.DateTime`
        """
        return self.shift(microseconds=-self.microsecond)

    def end_of_century(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the century of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(years=-(self.year % 100) + (count * 100),
                           months=-self.month + 1,
                           days=-self.day + 1,
                           hours=-self.hour,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_decade(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the decade of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(years=-(self.year % 10) + (count * 10),
                           months=-self.month + 1,
                           days=-self.day + 1,
                           hours=-self.hour,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_year(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the year of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(years=count,
                           months=-self.month + 1,
                           days=-self.day + 1,
                           hours=-self.hour,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_month(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the month of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(months=count,
                           days=-self.day + 1,
                           hours=-self.hour,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_day(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the day of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(days=count,
                           hours=-self.hour,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_hour(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the hour of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(hours=count,
                           minutes=-self.minute,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_minute(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the minute of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(minutes=count,
                           seconds=-self.second,
                           microseconds=-1))

    def end_of_second(self, count=1):
        """Return a new :class:`.DateTime` set to the end of the second of
        this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        return (self.start_of_second()
                    .shift(seconds=count,
                           microseconds=-1))

    def validate_frame(self, frame):
        """Validates the given time frame."""
        attrs = ['century',
                 'decade',
                 'year',
                 'month',
                 'day',
                 'hour',
                 'minute',
                 'second']

        if frame not in attrs:
            raise ValueError('The given time frame {0} is invalid'
                             .format(frame))

    def start_of(self, frame):
        """Return the start of the given time frame for this datetime.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).

        Returns:
            :class:`.DateTime`
        """
        self.validate_frame(frame)
        return getattr(self, 'start_of_{0}'.format(frame))()

    def end_of(self, frame, count=1):
        """Return the end of a given time frame for this datetime.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            count (int): Number of frames to span.

        Returns:
            :class:`.DateTime`
        """
        self.validate_frame(frame)
        return getattr(self, 'end_of_{0}'.format(frame))(count)

    def span(self, frame, count=1):
        """Returns two new :class:`.DateTime` objects corresponding to the time
        span between this object and the given time frame.

        Args
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            count (int): Number of frames to span.

        Returns:
            tuple: (`start_of_frame`, `end_of_frame`)
        """
        return (self.start_of(frame), self.end_of(frame, count))

    def __repr__(self):  # pragma: no cover
        """Return representation of :class:`.DateTime`."""
        return '<DateTime [{0}]>'.format(self.isoformat())

    def __str__(self):
        """Return :class:`.DateTime` instance as an ISO 8601 string."""
        return self.isoformat()

    def __iter__(self):
        """Return :class:`.DateTime` instance as an iterator that yields a tuple
        corresponding to
        ``(year, month, day, hour, minute, second, microsecond, tzinfo)``.
        """
        return iter((self.year,
                     self.month,
                     self.day,
                     self.hour,
                     self.minute,
                     self.second,
                     self.microsecond,
                     self.tzinfo))

    def __sub__(self, other):
        """Subtract a ``timedelta``, ``datetime``, or :class:`.DateTime` and
        return the result.

        Returns:
            :class:`.DateTime`: if subtracting a :class:`timedelta`
            :class:`timedelta`: if subtracting a :class:`datetime` or
                :class:`.DateTime`
        """
        if not isinstance(other, DateTime) and isinstance(other, datetime):
            other = self.fromdatetime(other)

        result = super(DateTime, self).__sub__(other)

        if isinstance(result, datetime):
            return self.fromdatetime(result)
        else:
            return result


#: Minimum DateTime value.
DateTime.min = DateTime(1, 1, 1)

#: Maximum DateTime value.
DateTime.max = DateTime(9999, 12, 31, 23, 59, 59, 999999)

#: DateTime value of EPOCH.
DateTime.epoch = DateTime(1970, 1, 1)
