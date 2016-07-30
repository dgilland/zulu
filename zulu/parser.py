# -*- coding: utf-8 -*-
"""The parser module.
"""

from __future__ import absolute_import

from functools import partial
from itertools import groupby
from datetime import datetime

import iso8601
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
    'ee': '%a',      # Weekday's abbreviated name
    'e': '%w',       # Weekday as decimal
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
    'ZZ': lambda value: value[:-2] + ':' + value[-2:]
}

# Pattern formatter functions that operate on the datetime object. These
# correspond to patterns that are not supported by stftime().
PATTERN_DATETIME_FORMATTERS = {
    'X': lambda dt: str((dt - EPOCH).total_seconds())  # Timestamp
}


class ParseError(Exception):
    """Exception raised when an object cannot be parsed as a datetime."""
    pass


def parse(obj, fmts=None, default_tz=None):
    """Attempt to parse `obj` as a ``datetime`` using  a list of `fmts`. If
    no timezone information is found in `obj` and `default_tz` is set, then
    the naive datetime object will be shifted to the default timezone.

    Args:
        obj (mixed): Object to parse.
        fmts (list, optional): List of string formats to use when parsing.
            Defaults to ``['ISO8601', 'timestamp']``.
        default_tz (None|str|tzinfo, optional): Default timezone to use when
            parsed datetime object does not contain a timezone. Defaults to
            ``UTC``.
    """
    if default_tz is None:
        default_tz = iso8601.UTC

    if not is_valid_timezone(default_tz):
        raise ValueError('Unrecognized timezone: {0}'.format(default_tz))

    if is_valid_datetime(obj):
        return obj

    if fmts is None:
        fmts = ['ISO8601', 'X']
    elif not isinstance(fmts, (list, tuple)):
        fmts = [fmts]

    dt = _parse_formats(obj, fmts)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not has_valid_timezone(dt):
        raise ParseError('Timezone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def _parse_formats(obj, fmts):
    """Parse `obj` as datetime using list of `fmts`."""
    dt = None
    errors = {}

    for fmt in fmts:
        try:
            dt = _parse_format(obj, fmt)
        except Exception as exc:
            errors[fmt] = str(exc)
            dt = None
        else:
            break

    if dt is None:
        err = ', '.join('"{0}" ({1})'.format(fmt, errors[fmt])
                        for fmt in fmts)
        raise ParseError('Value "{0}" does not match any format in {1}'
                         .format(obj, err))

    return dt


def _parse_format(obj, fmt):
    """Parse `obj` as datetime using `fmt`."""
    if fmt.upper() == 'ISO8601':
        return iso8601.parse_date(obj, default_timezone=None)
    elif fmt == 'X':
        return datetime.fromtimestamp(obj, pytz.UTC)
    else:
        if '%' not in fmt:
            fmt = _date_pattern_to_directive(fmt)
        return datetime.strptime(obj, fmt)


def format(dt, fmt=None, tz=None):
    """Return string formatted datetime, `dt`, using format directives or
    pattern in `fmt`. If timezone, `tz`, is supplied, the datetime will be
    shifted to that timezone before being formatted.

    Args:
        dt (datetime): A datetime instance.
        fmt (str, optional): Datetime format string. Defaults to ``None`` which
            uses ISO-8601 format.
        tz (None|str|tzinfo, optional): Timezone to shift `dt` to before
            formatting.

    Returns:
        str
    """
    if not isinstance(dt, datetime):
        raise TypeError("zulu.parser.format()'s first argument must be a "
                        "datetime, not {0}"
                        .format(type(dt)))  # pragma: no cover

    if fmt is not None and not isinstance(fmt, string_types):
        raise TypeError("zulu.parser.format()'s second argument must be a "
                        "string or None, not {0}"
                        .format(type(fmt)))  # pragma: no cover

    if not is_valid_timezone(tz):  # pragma: no cover
        raise ValueError('Unrecognized timezone: {0}'.format(tz))

    if tz is not None:
        dt = dt.astimezone(tz)

    if fmt is None:
        return dt.isoformat()
    elif '%' not in fmt:
        return _format_date_pattern(dt, fmt)
    else:
        return dt.strftime(fmt)


def _format_date_pattern(dt, fmt):
    """Format datetime, `dt`, using date-pattern format, `fmt`."""
    formatted = ''

    for token in _tokenize_date_pattern(fmt):
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


def _date_pattern_to_directive(fmt):
    """Convert date pattern format to strptime/strftime directives."""
    return ''.join(DATE_PATTERN_TO_DIRECTIVE.get(token, token)
                   for token in _tokenize_date_pattern(fmt))


def _tokenize_date_pattern(fmt):
    """Return list of date pattern tokens.

    This groups tokens by repeating characters so that each set of repeating
    characters is a list item (e.g. ``'YY-MM-dd'`` becomes
    ``['YY', '-', 'MM', '-', 'dd']``).
    """
    return [''.join(group) for key, group in groupby(fmt)]


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
