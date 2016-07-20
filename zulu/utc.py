# -*- coding: utf-8 -*-
"""The datetime module.
"""

from datetime import datetime, timedelta
from functools import wraps

from babel.dates import format_datetime
import pytz
import tzlocal

from .parser import parse


class _Missing(object):
    """Represents an unset value."""
    pass


Missing = _Missing()


class DateTime(object):
    def __init__(self,
                 year,
                 month,
                 day,
                 hour=0,
                 minute=0,
                 second=0,
                 microsecond=0,
                 tzinfo=None):
        if tzinfo and isinstance(tzinfo, str):
            tzinfo = make_timezone(tzinfo)

        naive = datetime(year, month, day, hour, minute, second, microsecond)

        if hasattr(tzinfo, 'localize'):
            dt = tzinfo.localize(naive, is_dst=None)
        elif tzinfo:
            dt = naive.replace(tzinfo=tzinfo)
        else:
            dt = pytz.UTC.localize(naive, is_dst=None)

        self.__dt = dt.astimezone(pytz.UTC)

    def __repr__(self):  # pragma: no cover
        return '<DateTime [{0}]>'.format(self.isoformat())

    def __iter__(self):
        return iter((self.year,
                     self.month,
                     self.day,
                     self.hour,
                     self.minute,
                     self.second,
                     self.microsecond,
                     self.tzinfo))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.datetime
        return self.datetime == other

    @classmethod
    def parse(cls, text):
        if isinstance(text, cls):
            dt = text.datetime
        elif is_valid_datetime(text):
            dt = text
        else:
            dt = parse(text)

        return cls.from_datetime(dt)

    @classmethod
    def from_datetime(cls, dt):
        return cls(dt.year,
                   dt.month,
                   dt.day,
                   dt.hour,
                   dt.minute,
                   dt.second,
                   dt.microsecond,
                   dt.tzinfo)

    @property
    def datetime(self):
        return self.__dt

    @property
    def tzinfo(self):
        return self.datetime.tzinfo

    @property
    def year(self):
        return self.datetime.year

    @property
    def month(self):
        return self.datetime.month

    @property
    def day(self):
        return self.datetime.day

    @property
    def hour(self):
        return self.datetime.hour

    @property
    def minute(self):
        return self.datetime.minute

    @property
    def second(self):
        return self.datetime.second

    @property
    def microsecond(self):
        return self.datetime.microsecond

    @property
    def naive(self):
        return self.datetime.replace(tzinfo=None)

    def localize(self, tzinfo=None):
        if tzinfo is None:
            tz = tzlocal.get_localzone()
        elif isinstance(tzinfo, str):
            tz = pytz.timezone(tzinfo)

        return self.datetime.astimezone(tz=tz)

    def isoformat(self, sep='T'):
        return self.datetime.isoformat(sep)

    def format(self, format=None, tzinfo=None, locale=None):
        if format is None:
            micro_fmt = '.SSSSSS' if self.microsecond > 0 else ''
            format = 'YYYY-MM-DDTHH:mm:ss{0}xxx'.format(micro_fmt)

        args = {}

        if tzinfo:
            args['tzinfo'] = tzinfo

        if locale:
            args['locale'] = locale

        return format_datetime(self.datetime, format, **args)

    def copy(self):
        return self.from_datetime(self.datetime)

    def offset(self,
               days=0,
               seconds=0,
               microseconds=0,
               milliseconds=0,
               minutes=0,
               hours=0,
               weeks=0):
        dt = self.datetime + timedelta(days,
                                       seconds,
                                       microseconds,
                                       milliseconds,
                                       minutes,
                                       hours,
                                       weeks)
        return self.from_datetime(dt)

    def replace(self,
                year=Missing,
                month=Missing,
                day=Missing,
                hour=Missing,
                minute=Missing,
                second=Missing,
                microsecond=Missing,
                tzinfo=Missing):
        args = {}

        if year is not Missing:
            args['year'] = year

        if month is not Missing:
            args['month'] = month

        if day is not Missing:
            args['day'] = day

        if hour is not Missing:
            args['hour'] = hour

        if minute is not Missing:
            args['minute'] = minute

        if second is not Missing:
            args['second'] = second

        if microsecond is not Missing:
            args['microsecond'] = microsecond

        if tzinfo is not Missing:
            args['tzinfo'] = make_timezone(tzinfo)

        return self.from_datetime(self.datetime.replace(**args))


def is_valid_datetime(obj):
    if isinstance(obj, datetime):
        return True
    else:
        attrs = ('year',
                 'month',
                 'day',
                 'hour',
                 'minute',
                 'second',
                 'microsecond',
                 'tzinfo')
        return all(hasattr(obj, attr) for attr in attrs)


def make_timezone(obj):
    # TODO: Improve default handling of non-strings?
    if isinstance(obj, str):
        tz = pytz.timezone(obj)
    else:
        tz = obj

    return tz
