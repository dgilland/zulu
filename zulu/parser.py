# -*- coding: utf-8 -*-
"""The parser module.
"""

from __future__ import absolute_import

from functools import partial
from itertools import groupby
from datetime import datetime, timedelta

from babel.dates import (
    LC_TIME,
    format_timedelta as _format_timedelta,
    format_datetime as _format_datetime
)
import iso8601
import pytimeparse
import pytz
import tzlocal

from ._compat import number_types, string_types


EPOCH = pytz.UTC.localize(datetime(1970, 1, 1), is_dst=None)

ISO8601 = 'ISO8601'
TIMESTAMP = 'timestamp'
DEFAULT_PARSE_DATETIME_FORMATS = (ISO8601, TIMESTAMP)


# Subset of Unicode date field patterns from:
# http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table
# that are supported as an alternative to Python's strptime/strftime
# directives. This mapping is used to convert the Unicode pattern (the dict
# keys) to the best matched strptime directive (the values). For values that
# are tuples, the first item is the directive used for string parsing while the
# second item is the directive used for string formatting. The second items are
# platform dependent and may not work on all systems.
DATE_PATTERN_TO_DIRECTIVE = {
    'YYYY': '%Y',    # Year with century
    'YY': '%y',      # Year without century
    'MMMM': '%B',    # Month's full name
    'MMM': '%b',     # Month's abbreviated name
    'MM': '%m',      # Month padded
    'M': '%m',       # Month not padded
    'DDD': '%j',     # Day of the year padded
    'DD': '%j',      # Day of the year padded
    'D': '%j',       # Day of the year not padded
    'dd': '%d',      # Day of the month padded
    'd': '%d',       # Day of the month not padded
    'EEEE': '%A',    # Weekday's full name
    'EEE': '%a',     # Weekday's abbreviated name
    'EE': '%a',      # Weekday's abbreviated name
    'E': '%a',       # Weekday's abbreviated name
    'eee': '%a',     # Weekday's abbreviated name
    'ee': '%w',      # Weekday as decimal padded
    'e': '%w',       # Weekday as decimal not padded
    'HH': '%H',      # Hour-24 padded
    'H': '%H',       # Hour-24 not padded
    'hh': '%I',      # Hour-12 padded
    'h': '%I',       # Hour-12 not padded
    'mm': '%M',      # Minute padded
    'm': '%M',       # Minute not padded
    'ss': '%S',      # Second padded
    's': '%S',       # Second not padded
    'SSSSSS': '%f',  # Microsecond padded
    'SSSSS': '%f',   # Microsecond padded
    'SSSS': '%f',    # Microsecond padded
    'SSS': '%f',     # Microsecond padded
    'SS': '%f',      # Microsecond padded
    'S': '%f',       # Microsecond not padded
    'a': '%p',       # am or pm
    'z': '%z',       # UTC offset without separator
    'Z': '%z',       # UTC offset without separator
}

TIMEDELTA_GRANULARITIES = ('second',
                           'minute',
                           'hour',
                           'day',
                           'week',
                           'month',
                           'year')

TIMEDELTA_FORMATS = ('long', 'short', 'narrow')


class ParseError(Exception):
    """Exception raised when an object cannot be parsed as a datetime."""
    pass


def parse_datetime(obj, formats=None, default_tz=None):
    """Attempt to parse `obj` as a ``datetime`` using  a list of `formats`. If
    no timezone information is found in `obj` and `default_tz` is set, then
    the naive datetime object will be shifted to the default timezone.

    Args:
        obj (str|datetime): Object to parse.
        formats (list, optional): List of string formats to use when parsing.
            Defaults to ``['ISO8601', 'X']``.
        default_tz (None|str|tzinfo, optional): Default timezone to use when
            parsed datetime object does not contain a timezone. Defaults to
            ``UTC``.

    Returns:
        datetime

    Raises:
        ValueError: When `default_tz` is an unrecognized timezone.
        ParseError: When `obj` can't be parsed as a datetime.
    """
    if default_tz is None:
        default_tz = iso8601.UTC

    if not is_valid_timezone(default_tz):
        raise ValueError('Unrecognized timezone: {0}'.format(default_tz))

    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = DEFAULT_PARSE_DATETIME_FORMATS
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = _parse_datetime_formats(obj, formats)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not has_valid_timezone(dt):
        raise ParseError('Timezone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def _parse_datetime_formats(obj, formats):
    """Parse `obj` as datetime using list of `formats`."""
    dt = None
    errors = {}

    for format in formats:
        try:
            dt = _parse_datetime_format(obj, format)
        except Exception as exc:
            errors[format] = str(exc)
            dt = None
        else:
            break

    if dt is None:
        err = ', '.join('"{0}" ({1})'.format(format, errors[format])
                        for format in formats)
        raise ParseError('Value "{0}" does not match any format in [{1}]'
                         .format(obj, err))

    return dt


def _parse_datetime_format(obj, format):
    """Parse `obj` as datetime using `format`."""
    if format.upper() == ISO8601:
        return iso8601.parse_date(obj, default_timezone=None)
    elif format.lower() == TIMESTAMP:
        return datetime.fromtimestamp(obj, pytz.UTC)
    else:
        if '%' not in format:
            format = _date_pattern_to_directive(format)
        return datetime.strptime(obj, format)


def format_datetime(dt, format=None, tz=None, locale=LC_TIME):
    """Return string formatted datetime, `dt`, using format directives or
    pattern in `format`. If timezone, `tz`, is supplied, the datetime will be
    shifted to that timezone before being formatted.

    Args:
        dt (datetime): A datetime instance.
        format (str, optional): Datetime format string. Defaults to ``None``
            which uses ISO-8601 format.
        tz (None|str|tzinfo, optional): Timezone to shift `dt` to before
            formatting.
        locale (str|Locale, optional): A ``Locale`` object or locale
            identifer. Defaults to system default.

    Returns:
        str
    """
    if not isinstance(dt, datetime):
        raise TypeError("zulu.parser.format()'s first argument must be a "
                        "datetime, not {0}"
                        .format(type(dt).__name__))  # pragma: no cover

    if format is not None and not isinstance(format, string_types):
        raise TypeError("zulu.parser.format()'s second argument must be a "
                        "string or None, not {0}"
                        .format(type(format).__name__))  # pragma: no cover

    if not is_valid_timezone(tz):  # pragma: no cover
        raise ValueError('Unrecognized timezone: {0}'.format(tz))

    if format is None:
        format = ISO8601

    if tz is not None:
        dt = dt.astimezone(tz)

    if format == ISO8601:
        return dt.isoformat()
    elif '%' in format:
        return dt.strftime(format)
    else:
        return _format_datetime(dt, format, locale=locale)


def _date_pattern_to_directive(format):
    """Convert date pattern format to strptime/strftime directives."""
    return ''.join(DATE_PATTERN_TO_DIRECTIVE.get(token, token)
                   for token in _tokenize_date_pattern(format))


def _tokenize_date_pattern(format):
    """Return list of date pattern tokens.

    This groups tokens by repeating characters so that each set of repeating
    characters is a list item (e.g. ``'YY-MM-dd'`` becomes
    ``['YY', '-', 'MM', '-', 'dd']``).
    """
    return [''.join(group) for key, group in groupby(format)]


def parse_timedelta(obj):
    """Attempt to parse `obj` as a ``timedelta`` from a string formatted
    duration.

    Args:
        obj (str|number|timedelta): Object to parse.

    Returns:
        timedelta

    Raises:
        TypeError: When `obj` is not a string or timedelta.
        ParseError: When `obj` can't be parsed as a timedelta.
    """
    if isinstance(obj, timedelta):
        return obj

    is_string = isinstance(obj, string_types)
    is_number = isinstance(obj, number_types)

    if not is_string and not is_number:
        raise TypeError('Expected string or number type, not {0}'
                        .format(type(obj).__name__))

    if is_string:
        seconds = pytimeparse.parse(obj)

        if seconds is None:
            raise ParseError('Value "{0}" is not a recognized duration format'
                             .format(obj))
    else:
        seconds = obj

    return timedelta(seconds=seconds)


def format_timedelta(delta,
                     format='long',
                     granularity='second',
                     threshold=0.85,
                     add_direction=False,
                     locale=LC_TIME):
    """Return timedelta as a formatted string.

    Args:
        format (str, optional): Can be one of "long", "short", or "narrow".
            Defaults to `'long`'.
        granularity (str, optional): The smallest unit that should be
            displayed. The value can be one of "year", "month", "week",
            "day", "hour", "minute" or "second". Defaults to `'second'`.
        threshold (float, optional): Factor that determines at which point
            the presentation switches to the next higher unit. Defaults to
            `0.85`.
        add_direction (bool, optional): If ``True`` the return value will
            include directional information (e.g. `'1 hour ago'`,
            `'in 1 hour'`). Defaults to ``False``.
        locale (str|Locale, optional): A ``Locale`` object or locale
            identifer. Defaults to system default.
    """
    if granularity not in TIMEDELTA_GRANULARITIES:
        grans = ', '.join('"{0}"'.format(gra)
                          for gra in TIMEDELTA_GRANULARITIES)
        raise ValueError('Time delta format granularity must be one of {0}, '
                         'not "{1}"'
                         .format(grans, granularity))

    if format not in TIMEDELTA_FORMATS:
        formats = ', '.join('"{0}"'.format(format)
                            for format in TIMEDELTA_FORMATS)
        raise ValueError('Time delta format must be one of {0}, not "{1}"'
                         .format(formats, format))

    return _format_timedelta(delta,
                             granularity=granularity,
                             threshold=threshold,
                             add_direction=add_direction,
                             format=format,
                             locale=locale)


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


def get_timestamp(dt):
    """Return timestamp for datetime, `dt`."""
    return (dt - EPOCH).total_seconds()


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


def is_valid_timezone(tz):
    try:
        get_timezone(tz)
    except Exception:
        return False
    else:
        return True


def has_valid_timezone(dt):
    """Return whether `tz` is a valid timezone with a UTC offset strictly
    between -24/+24 hours.

    Returns:
        bool
    """
    try:
        dt.astimezone(pytz.UTC)
    except Exception:
        return False
    else:
        return True
