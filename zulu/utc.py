# -*- coding: utf-8 -*-
"""The UTC module.
"""

from datetime import datetime, timedelta
from functools import wraps

import pytz
import tzlocal

from .parser import get_timezone, parse
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
                year,
                month,
                day,
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
        return super(DateTime, self).replace(tzinfo=None)

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
              days=0,
              seconds=0,
              microseconds=0,
              milliseconds=0,
              minutes=0,
              hours=0,
              weeks=0):
        """Shift datetime using a timedelta created from the supplied
        arguments and return a new :class:`.DateTime` instance.

        Returns:
            :class:`.DateTime`
        """
        dt = self + timedelta(days,
                              seconds,
                              microseconds,
                              milliseconds,
                              minutes,
                              hours,
                              weeks)
        return self.fromdatetime(dt)

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
