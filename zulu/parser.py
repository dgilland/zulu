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
    pass


def parse(obj, formats=None, default_tz=None):
    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = ['ISO8601', 'timestamp']
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = parse_formats(obj, formats)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not is_valid_timezone(dt.tzinfo):
        raise ParseError('Time zone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def parse_formats(obj, formats):
    dt = None

    for format in formats:
        try:
            dt = parse_format(obj, format)
        except Exception:
            dt = None
        else:
            break

    if dt is None:
        raise ParseError('Value "{0}" does not match any format in {1}'
                         .format(obj, formats))

    return dt


def parse_format(obj, format):
    if format.upper() == 'ISO8601':
        return iso8601.parse_date(obj, default_timezone=None)
    elif format == 'timestamp':
        return datetime.fromtimestamp(obj, pytz.UTC)
    else:
        return datetime.strptime(obj, format)


    if tz == 'local':
        tz = tzlocal.get_localzone()
    elif isinstance(tz, string_types):
        tz = pytz.timezone(tz)

    return tz


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


def is_valid_timezone(tzinfo):
    if tzinfo is None:
        return True

    if not callable(getattr(tzinfo, 'utcoffset', None)):  # pragma: no cover
        return False

    if hasattr(tzinfo, '_utcoffset'):
        utcoffset = tzinfo._utcoffset
    else:
        utcoffset = tzinfo.utcoffset(tzinfo)

    return abs(utcoffset) < MAX_TIMEZONE_OFFSET
