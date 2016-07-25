# -*- coding: utf-8 -*-
"""The UTC module.
"""

from datetime import datetime, timedelta
from functools import wraps

import pytz
import tzlocal

from .parser import get_timezone, parse
from .utils import Missing
from ._compat import string_types


class DateTime(object):
    """The DateTime class represents an immutable UTC datetime object. Any
    timezone information given to it during instantiation results in the
    datetime object being converted from that timezone to UTC. If timezone
    information is not given, then it's assumed the datetime is a UTC value.
    All arthimetic is perform on the underlying UTC datetime object. DateTime
    has no concept of timezone shifting in this regard. Instead, localization
    occurs only when formatting a DateTime object as a string.

    The DateTime class has a drop-in replacement API for a datetime instance
    from the Standard Library, but does not represent itself in any timezone
    other than UTC.

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
    def __init__(self,
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

        self.__dt = dt.astimezone(pytz.UTC)

    @classmethod
    def now(cls):
        """Return the current UTC date and time as :class:`DateTime` object.

        Returns:
            DateTime
        """
        return cls.fromdatetime(datetime.utcnow())

    @classmethod
    def parse(cls, obj, formats=None, default_tz=None):
        """Return :class:`DateTime` object parsed from `obj`.

        Args:
            obj (mixed): Object to parse into a :class:`DateTime` object.
            formats (list, optional): List of string formats to use when
                parsing. Defaults to ``['ISO8601', 'timestamp']``.
            default_tz (None|str|tzinfo, optional): Default timezone to use
                when parsed datetime object does not contain a timezone.
                Defaults to ``UTC``.

        Returns:
            DateTime
        """
        dt = parse(obj, formats=formats, default_tz=default_tz)
        return cls.fromdatetime(dt)

    @classmethod
    def fromdatetime(cls, dt):
        """Return :class:`DateTime` object from a Standard Library datetime
        object.

        Returns:
            DateTime
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
    def fromtimestamp(cls, timestamp):
        """Return :class:`DateTime` object from a POSIX timestamp.

        Args:
            timestamp (int): POSIX timestamp such as is returned by
                ``time.time()``.

        Returns:
            DateTime
        """
        return cls.fromdatetime(datetime.fromtimestamp(timestamp, pytz.UTC))

    @classmethod
    def fromordinal(cls, ordinal):
        """Return :class:`DateTime` object from a proleptic Gregorian ordinal,
        where January 1 of year 1 has ordinal 1.

        Args:
            ordinal (int): A proleptic Gregorian ordinal.

        Returns:
            DateTime
        """
        return cls.fromdatetime(datetime.fromordinal(ordinal))

    @classmethod
    def combine(cls, date, time):
        """Return :class:`DateTime` object by combining the date part from
        `date` and the time part from `time`.

        Args:
            date (mixed): Either a :class:`DateTime`, ``datetime.date``,
                or ``datetime.datetime`` object to use as the date part.
            date (mixed): Either a :class:`DateTime` or ``datetime.time``
                object to use as the time part.

        Returns:
            DateTime
        """
        if callable(getattr(date, 'date', None)):
            date = date.date()

        if callable(getattr(time, 'time', None)):
            time = time.time()

        return cls.fromdatetime(datetime.combine(date, time))

    @property
    def datetime(self):
        """The underlying Standard Library datetime object."""
        return self.__dt

    @property
    def year(self):
        """The datetime year."""
        return self.datetime.year

    @property
    def month(self):
        """The datetime month."""
        return self.datetime.month

    @property
    def day(self):
        """The datetime day."""
        return self.datetime.day

    @property
    def hour(self):
        """The datetime hour."""
        return self.datetime.hour

    @property
    def minute(self):
        """The datetime minute."""
        return self.datetime.minute

    @property
    def second(self):
        """The datetime second."""
        return self.datetime.second

    @property
    def microsecond(self):
        """The datetime microsecond."""
        return self.datetime.microsecond

    @property
    def tzinfo(self):
        """The datetime tzinfo."""
        return self.datetime.tzinfo

    @property
    def naive(self):
        """The datetime object as a naive datetime (tzinfo=None)."""
        return self.datetime.replace(tzinfo=None)

    def timestamp(self):
        """Return the POSIX timestamp of :attr:`datetime`.

        Returns:
            int
        """
        return (self - _EPOCH).total_seconds()

    def utcoffset(self):
        """Return the UTC offset of :attr:`datetime`.

        Returns:
            timedelta
        """
        return self.datetime.utcoffset()

    def dst(self):
        """Return the DST of :attr:`datetime`.

        Returns:
            timedelta
        """
        return self.datetime.dst()

    def tzname(self):
        """Return the timezone name of :attr:`datetime`.

        Returns:
            str
        """
        return self.datetime.tzname()

    def date(self):
        """Return the date part of :attr:`datetime`.

        Returns:
            date
        """
        return self.datetime.date()

    def time(self):
        """Return the time part of :attr:`datetime` with tzinfo unset
        (``None``).

        Returns:
            time
        """
        return self.datetime.time()

    def timetz(self):
        """Return the time part of :attr:`datetime` with tzinfo set.

        Returns:
            time
        """
        return self.datetime.timetz()

    def weekday(self):
        """Return the weekday of :attr:`datetime` where Monday is 0 and Sunday
        is 6.

        Returns:
            int
        """
        return self.datetime.weekday()

    def isoweekday(self):
        """Return the isoweekday of :attr:`datetime` where Monday is 1 and
        Sunday is 7.

        Returns:
            int
        """
        return self.datetime.isoweekday()

    def isocalendar(self):
        """Return a 3-tuple (ISO year, ISO week number, ISO weekday) of
        :attr:`datetime`.

        Returns:
            tuple
        """
        return self.datetime.isocalendar()

    def ctime(self):
        """Return the date and time string of :attr:`datetime` that conforms to
        the C standard format.

        Returns:
            str
        """
        return self.datetime.ctime()

    def toordinal(self):
        """Return the proleptic Gregorian ordinal of the date of
        :attr:`datetime`.
        """
        return self.datetime.toordinal()

    def timetuple(self):
        """Return a ``time.struct_time`` object of :attr:`datetime`.

        Returns:
            time.struct_time
        """
        return self.datetime.timetuple()

    def isoformat(self, sep='T'):
        """Return :attr:`datetime` in ISO 8601 format,
        ``YYYY-MM-DDTHH:MM:SS.mmmmmm`` or, if :attr:`microsecond` is 0,
        ``YYYY-MM-DDTHH:MM:SS``.

        Arg:
            sep (str, optional): Separator to use between date and time parts.
                Defaults to ``'T'``.

        Returns:
            str
        """
        return self.datetime.isoformat(sep)

    def copy(self):
        """Return a new :class`DateTime` instance with the same
        :attr:`datetime` value.

        Returns:
            DateTime
        """
        return self.fromdatetime(self.datetime)

    def strftime(self, format):
        """Return :attr:`datetime` as a string using the format string
        `format`.

        Returns:
            str
        """
        return self.datetime.strftime(format)

    def format(self, format=None, tz=None):
        """Return :attr:`datetime` as a string using the format string `format`
        while optionally converting to timezone `tz` first.

        Args:
            format (str): Format to return string in. If ``None``, ISO 8601
                format is used. Defaults to ``None``.
            tz (None|str|tzinfo, optional): Timezone to convert to before
                formatting. Defaults to ``None``.

        Returns:
            str
        """
        if tz is not None:
            dt = self.astimezone(tz)
        else:
            dt = self.datetime

        if format is None:
            return dt.isoformat()
        else:
            return dt.strftime(format)

    def astimezone(self, tz='local'):
        """Return :attr:`datetime` shifted to timezone `tz`.

        .. note:: This returns a Standard Library datetime object.

        Args:
            tz (None|str|tzinfo, optional): Timezone to shift to.

        Returns:
            datetime
        """
        if tz is None:
            tz = 'local'
        tz = get_timezone(tz)
        return self.datetime.astimezone(tz)

    def offset(self,
               days=0,
               seconds=0,
               microseconds=0,
               milliseconds=0,
               minutes=0,
               hours=0,
               weeks=0):
        """Apply an offset to :attr:`datetime` and return a new
        :class:`DateTime` instance.

        Returns:
            DateTime
        """
        dt = self.datetime + timedelta(days,
                                       seconds,
                                       microseconds,
                                       milliseconds,
                                       minutes,
                                       hours,
                                       weeks)
        return self.fromdatetime(dt)

    def replace(self,
                year=Missing,
                month=Missing,
                day=Missing,
                hour=Missing,
                minute=Missing,
                second=Missing,
                microsecond=Missing,
                tzinfo=Missing):
        """Replace :attr:`datetime` attributes and return a new
        :class:`DateTime` instance.

        Returns:
            DateTime
        """
        args = list(self)

        if year is not Missing:
            args[0] = year

        if month is not Missing:
            args[1] = month

        if day is not Missing:
            args[2] = day

        if hour is not Missing:
            args[3] = hour

        if minute is not Missing:
            args[4] = minute

        if second is not Missing:
            args[5] = second

        if microsecond is not Missing:
            args[6] = microsecond

        if tzinfo is not Missing:
            args[7] = tzinfo

        return DateTime(*args)

    def __repr__(self):  # pragma: no cover
        """Return representation of :class:`DateTime`."""
        return '<DateTime [{0}]>'.format(self.isoformat())

    def __str__(self):
        """Return :class:`DateTime` instance as an ISO 8601 string."""
        return self.isoformat()

    def __format__(self, fmt):
        """Same as :meth:`strftime`. This makes it possible to specify a format
        string for a datetime object when using ``str.format()``.
        """
        if not isinstance(fmt, str):  # pragma: no cover
            raise TypeError('must be str, not %s' % type(fmt).__name__)
        if len(fmt) != 0:
            return self.format(fmt)
        return str(self)

    def __iter__(self):
        """Return :class:`DateTime` instance as an iterator that yields a tuple
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

    def __eq__(self, other):
        """Return whether :attr:`datetime` is equal to `other`."""
        return self.datetime == _get_comparison_value(other)

    def __ne__(self, other):
        """Return whether :attr:`datetime` is not equal to `other`."""
        return self.datetime != _get_comparison_value(other)

    def __le__(self, other):
        """Return whether :attr:`datetime` is less than or equal to `other`."""
        return self.datetime <= _get_comparison_value(other)

    def __lt__(self, other):
        """Return whether :attr:`datetime` is less than `other`."""
        return self.datetime < _get_comparison_value(other)

    def __ge__(self, other):
        """Return whether :attr:`datetime` is greater than or equal to
        `other`."""
        return self.datetime >= _get_comparison_value(other)

    def __gt__(self, other):
        """Return whether :attr:`datetime` is greater than `other`."""
        return self.datetime > _get_comparison_value(other)

    def __add__(self, other):
        """Add a ``timedelta`` to :attr:`datetime` and return a new
        :class:`DateTime` instance.

        Returns:
            DateTime
        """
        return self.fromdatetime(self.datetime + other)

    __radd__ = __add__

    def __sub__(self, other):
        """Subtract a ``timedelta``, ``datetime``, or :class:`DateTime` and
        return the result.

        Returns:
            DateTime: if subtracting a ``timedelta``
            timedelta: if subtracting a ``datetime`` or :class:`DateTime`
        """
        if isinstance(other, DateTime):
            other = other.datetime
        elif isinstance(other, datetime):
            other = self.fromdatetime(other).datetime

        result = self.datetime - other

        if isinstance(result, datetime):
            return self.fromdatetime(result)
        else:
            return result

    def __hash__(self):
        """Return hash() of :attr:`datetime`."""
        return hash(self.datetime)

    # TODO: Pickle support?


_EPOCH = DateTime(1970, 1, 1)


def _get_comparison_value(other):
    if isinstance(other, DateTime):
        other = other.datetime
    return other
