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


try:
    datetime.utcnow().strftime('%-S')
except Exception:  # pragma: no cover
    # Platform cannot use '%-' format directives for removing leading zeros.
    _ENHANCED_FORMATTING_SUPPORTED = False
else:  # pragma: no cover
    # Platform supports '%-' format directives for removing leading zeros.
    _ENHANCED_FORMATTING_SUPPORTED = True


# Subset of Unicode date field patterns from:
# http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table
# that are supported as an alternative to Python's strptime/strftime
# directives. This mapping is used to convert the Unicode pattern (the dict
# keys) to the best matched strptime directive (the values). For values that
# are tuples, the first item is the directive used for string parsing while the
# second item is the directive used for string formatting. The second items are
# platform dependent and may not work on all systems.
DATE_PATTERN_TO_DIRECTIVE = {
    'YYYY': '%Y',          # Year with century
    'YY': '%y',            # Year without century
    'MMMM': '%B',          # Month's full name
    'MMM': '%b',           # Month's abbreviated name
    'MM': '%m',            # Month padded
    'M': ('%m', '%-m'),    # Month not padded
    'DDD': '%j',           # Day of the year padded
    'D': ('%j', '%-j'),    # Day of the year not padded
    'dd': '%d',            # Day of the month padded
    'd': ('%d', '%-d'),    # Day of the month not padded
    'EEEE': '%A',          # Weekday's full name
    'EEE': '%a',           # Weekday's abbreviated name
    'EE': '%a',            # Weekday's abbreviated name
    'E': '%a',             # Weekday's abbreviated name
    'eee': '%a',           # Weekday's abbreviated name
    'ee': '%a',            # Weekday's abbreviated name
    'e': '%w',             # Weekday as decimal
    'HH': '%H',            # Hour-24 padded
    'H': ('%H', '%-H'),    # Hour-24 not padded
    'hh': '%I',            # Hour-12 padded
    'h': ('%I', '%-I'),    # Hour-12 not padded
    'mm': '%M',            # Minute padded
    'm': ('%M', '%-M'),    # Minute not padded
    'ss': '%S',            # Second padded
    's': ('%S', '%-S'),    # Second not padded
    'SSSSSS': '%f',        # Microsecond padded
    'SSSSS': '%f',         # Microsecond padded
    'SSSS': '%f',          # Microsecond padded
    'SSS': '%f',           # Microsecond padded
    'SS': '%f',            # Microsecond padded
    'S': '%f',             # Microsecond not padded
    'a': '%p',             # AM or PM
    'Z': '%z',             # UTC offset without separator
}


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
    if default_tz is None:
        default_tz = iso8601.UTC

    if not is_valid_timezone(default_tz):
        raise ValueError('Unrecognized timezone given to use as default: {0}'
                         .format(default_tz))

    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = ['ISO8601', 'timestamp']
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = _parse_formats(obj, formats)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not has_valid_timezone(dt):
        raise ParseError('Timezone offset must be strictly between -24/+24 '
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
        err = ', '.join('"{0}" ({1})'.format(fmt, errors[fmt])
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
        if '%' not in format:
            format = _pattern_to_directive_parsing(format)
        return datetime.strptime(obj, format)


def _pattern_to_directive_parsing(format):
    """Translate a pattern format into a strptime directive format string."""
    return _translate_parse_format(format,
                                   mapping=DATE_PATTERN_TO_DIRECTIVE,
                                   token_index=0)


def _pattern_to_directive_formatting(format):
    """Translate a pattern format into a strftime directive format string."""
    return _translate_parse_format(format,
                                   mapping=DATE_PATTERN_TO_DIRECTIVE,
                                   token_index=1)


def _translate_parse_format(format, mapping, token_index=0):
    """Translate a parse `format` using `mapping` ``dict`` where the keys of
    `mapping` corresponding to possible tokens that would be found in `format`
    and the values of `mapping` corresponding to what should be substituted for
    those tokens. If the translated token value in `mapping` is a tuple, then
    `token_index` will be used to index into that tuple and substitute its
    value.
    """
    if not _ENHANCED_FORMATTING_SUPPORTED:  # pragma: no cover
        token_index = 0

    # This groups tokens by repeating characters so that each set of repeating
    # characters is a list item.
    # (e.g. 'YY-MM-dd' becomes ['YY', '-', 'MM', '-', 'dd'])
    tokens = [''.join(group) for key, group in groupby(format)]

    for idx, token in enumerate(tokens):
        if token not in mapping:
            continue

        mapped = mapping[token]

        if isinstance(mapped, tuple):
            # Get indexed value from tuple in cases where a token can be
            # translated to different values depending on the context.
            mapped = mapped[token_index]

        tokens[idx] = mapped

    return ''.join(tokens)


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
