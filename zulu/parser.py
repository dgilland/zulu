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


def parse(obj, formats=None):
    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = ['iso8601']
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = parse_formats(obj, formats)

    if not is_valid_timezone(dt.tzinfo):
        raise ParseError('Time zone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def parse_formats(string, formats):
    dt = None

    for format in formats:
        try:
            dt = parse_format(string, format)
        except Exception:
            dt = None
        else:
            break

    if dt is None:
        raise ParseError('Value "{0}" does not match any format in {1}'
                         .format(string, formats))

    return dt


def parse_format(string, format):
    if format == 'iso8601':
        return iso8601.parse_date(string, default_timezone=None)
    else:
        return datetime.strptime(string, format)


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
    return (tzinfo is None or
            abs(tzinfo.utcoffset(tzinfo)) < MAX_TIMEZONE_OFFSET)
