# -*- coding: utf-8 -*-
"""The parser module.
"""

from datetime import datetime, timedelta

import iso8601
import pytz
import tzlocal

from ._compat import string_types


MAX_TIMEZONE_OFFSET = timedelta(hours=24)


class ParseError(Exception):
    """Exception raised when an object cannot be parsed as a datetime."""
    pass


def parse(obj, formats=None, default_tz=None):
    """Attempt to parse `obj` as a ``datetime`` using  a list of `formats`. If
    no timezone information is found in `obj` and `default_tz` is set, then
    the naive datetime object will be shifted to the default timezone.

    Args:
        obj (mixed): Object to parse.
        formats (list, optional): List of string formats to use when parsing.
            Defaults to ``['ISO8601', 'timestamp']``.
        default_tz (None|str|tzinfo, optional): Default timezone to use when
            parsed datetime object does not contain a timezone. Defaults to
            ``UTC``.
    """
    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = ['ISO8601', 'timestamp']
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = _parse_formats(obj, formats)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not is_valid_timezone(dt.tzinfo):
        raise ParseError('Time zone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def _parse_formats(obj, formats):
    """Parse `obj` as datetime using list of `formats`."""
    dt = None
    errors = {}

    for format in formats:
        try:
            dt = _parse_format(obj, format)
        except Exception as exc:
            errors[format] = str(exc)
            dt = None
        else:
            break

    if dt is None:
        err = ', '.join('{0} ({1})'.format(fmt, errors[fmt])
                        for fmt in formats)
        raise ParseError('Value "{0}" does not match any format in {1}'
                         .format(obj, err))

    return dt


def _parse_format(obj, format):
    """Parse `obj` as datetime using `format`."""
    if format.upper() == 'ISO8601':
        return iso8601.parse_date(obj, default_timezone=None)
    elif format == 'timestamp':
        return datetime.fromtimestamp(obj, pytz.UTC)
    else:
        return datetime.strptime(obj, format)


def get_timezone(tz):
    """Coerce `tz` into a `tzinfo` compatible object. If ``tz == 'local'``,
    then the system's local timezone will be used. If `tz` is a string other
    than ``'local'``, it will be passed to ``pytz.timezone(tz)``. Otherwise,
    `tz` will be returned as-is.
    """
    if tz == 'local':
        tz = tzlocal.get_localzone()
    elif isinstance(tz, string_types):
        tz = pytz.timezone(tz)

    return tz


def is_valid_datetime(obj):
    """Return whether `obj` is an instance of ``datetime`` or contains date and
    time attributes.

    Returns:
        bool
    """
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


def is_valid_timezone(tzinfo):
    """Return whether `tz` is a valid timezone with a UTC offset strictly
    between -24/+24 hours.

    Returns:
        bool
    """
    if tzinfo is None:
        return True

    if not callable(getattr(tzinfo, 'utcoffset', None)):  # pragma: no cover
        return False

    if hasattr(tzinfo, '_utcoffset'):
        utcoffset = tzinfo._utcoffset
    else:
        utcoffset = tzinfo.utcoffset(tzinfo)

    return abs(utcoffset) < MAX_TIMEZONE_OFFSET
