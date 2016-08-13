# -*- coding: utf-8 -*-
"""The parser module.
"""

from __future__ import absolute_import

from functools import partial
from itertools import groupby
from datetime import datetime, timedelta

from babel.dates import format_timedelta as _format_timedelta
import iso8601
import pytimeparse
import pytz
import tzlocal

from ._compat import string_types


def _truncate(value, length):
    return value[:length]


def _remove_leading_zero(value, count=1):
    for _ in range(count):
        if value.startswith('0'):
            value = value[1:]
    return value


EPOCH = pytz.UTC.localize(datetime(1970, 1, 1), is_dst=None)

ISO8601 = 'ISO8601'
TIMESTAMP = 'X'
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
    'A': '%p',       # AM or PM
    'a': '%p',       # am or pm
    'Z': '%z',       # UTC offset without separator
    'ZZ': '%z',      # UTC offset with separator
}

# Transform functions to apply to strftime() output from these date patterns.
# These are use to modify strftime() output for cases where strftime() cannot
# produce the desired output but can produce something that can be transformed
# in the what's expected.
PATTERN_FORMAT_TRANSFORMS = {
    'M': _remove_leading_zero,
    'DD': partial(_remove_leading_zero, count=1),
    'D': partial(_remove_leading_zero, count=2),
    'd': _remove_leading_zero,
    'ee': lambda value: '0{0}'.format(value),
    'H': _remove_leading_zero,
    'h': _remove_leading_zero,
    'm': _remove_leading_zero,
    's': _remove_leading_zero,
    'SSSSS': partial(_truncate, length=5),
    'SSSS': partial(_truncate, length=4),
    'SSS': partial(_truncate, length=3),
    'SS': partial(_truncate, length=2),
    'S': partial(_truncate, length=1),
    'A': lambda value: value.upper(),
    'a': lambda value: value.lower(),
    'ZZ': lambda value: value[:-2] + ':' + value[-2:],
}

# Pattern formatter functions that operate on the datetime object. These
# correspond to patterns that are not supported by stftime().
PATTERN_DATETIME_FORMATTERS = {
    'XX': lambda dt: str(get_timestamp(dt)),      # Timestamp float
    'X': lambda dt: str(int(get_timestamp(dt))),  # Timestamp integer
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
        raise ParseError('Value "{0}" does not match any format in {1}'
                         .format(obj, err))

    return dt


def _parse_datetime_format(obj, format):
    """Parse `obj` as datetime using `format`."""
    if format.upper() == ISO8601:
        return iso8601.parse_date(obj, default_timezone=None)
    elif format.upper() == TIMESTAMP:
        return datetime.fromtimestamp(obj, pytz.UTC)
    else:
        if '%' not in format:
            format = _date_pattern_to_directive(format)
        return datetime.strptime(obj, format)


def parse_timedelta(obj):
    """Attempt to parse `obj` as a ``timedelta`` from a string formatted
    duration.

    Args:
        obj (str|timedelta): Object to parse.

    Returns:
        timedelta

    Raises:
        TypeError: When `obj` is not a string or timedelta.
        ParseError: When `obj` can't be parsed as a timedelta.
    """
    if isinstance(obj, timedelta):
        return obj

    if not isinstance(obj, string_types):
        raise TypeError('Expected string object, not {0}'.format(type(obj)))

    seconds = pytimeparse.parse(obj)

    if seconds is None:
        raise ParseError('Value "{0}" is not a recognized duration format')

    return timedelta(seconds=seconds)


def format_datetime(dt, format=None, tz=None):
    """Return string formatted datetime, `dt`, using format directives or
    pattern in `format`. If timezone, `tz`, is supplied, the datetime will be
    shifted to that timezone before being formatted.

    Args:
        dt (datetime): A datetime instance.
        format (str, optional): Datetime format string. Defaults to ``None``
            which uses ISO-8601 format.
        tz (None|str|tzinfo, optional): Timezone to shift `dt` to before
            formatting.

    Returns:
        str
    """
    if not isinstance(dt, datetime):
        raise TypeError("zulu.parser.format()'s first argument must be a "
                        "datetime, not {0}"
                        .format(type(dt)))  # pragma: no cover

    if format is not None and not isinstance(format, string_types):
        raise TypeError("zulu.parser.format()'s second argument must be a "
                        "string or None, not {0}"
                        .format(type(format)))  # pragma: no cover

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
        return _format_date_pattern(dt, format)


def _format_date_pattern(dt, format):
    """Format datetime, `dt`, using date-pattern format, `format`."""
    formatted = ''

    for token in _tokenize_date_pattern(format):
        if token in DATE_PATTERN_TO_DIRECTIVE:
            value = dt.strftime(DATE_PATTERN_TO_DIRECTIVE[token])
        else:
            value = token

        if token in PATTERN_FORMAT_TRANSFORMS:
            value = PATTERN_FORMAT_TRANSFORMS[token](value)
        elif token in PATTERN_DATETIME_FORMATTERS:
            value = PATTERN_DATETIME_FORMATTERS[token](dt)

        formatted += value

    return formatted


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


def format_timedelta(delta,
                     granularity='second',
                     threshold=0.85,
                     add_direction=False,
                     format='long'):
    """Return timedelta as a formatted string.

    Args:
        granularity (str, optional): The smallest unit that should be
            displayed. The value can be one of "year", "month", "week",
            "day", "hour", "minute" or "second". Defaults to `'second'`.
        threshold (float, optional): Factor that determines at which point
            the presentation switches to the next higher unit. Defaults to
            `0.85`.
        add_direction (bool, optional): If ``True`` the return value will
            include directional information (e.g. `'1 hour ago'`,
            `'in 1 hour'`). Defaults to ``False``.
        format (str, optional): Can be one of "long", "short", or "narrow".
            Defaults to `'long`'.
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
                             format=format)


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
