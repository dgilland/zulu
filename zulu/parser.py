# -*- coding: utf-8 -*-
"""The parser module.
"""

from datetime import timedelta

import iso8601


MAX_TIMEZONE_OFFSET = timedelta(hours=24)


class ParseError(Exception):
    pass


def parse(text, format=None):
    try:
        dt = iso8601.parse_date(text, default_timezone=None)
    except iso8601.ParseError as exc:
        raise ParseError(str(exc))

    if not is_valid_timezone(dt.tzinfo):
        raise ParseError('Time zone offset must be strictly between -24/+24 '
                         'hours')

    return dt


def is_valid_timezone(tzinfo):
    return (tzinfo is None or
            abs(tzinfo.utcoffset(tzinfo)) < MAX_TIMEZONE_OFFSET)
