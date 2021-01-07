"""The parser module."""

from datetime import datetime, timedelta
from itertools import groupby

from babel.dates import (
    LC_TIME,
    format_datetime as _format_datetime,
    format_timedelta as _format_timedelta,
)
from dateutil.tz import gettz, tzlocal, tzutc
import iso8601
import pytimeparse

from .helpers import NUMBER_TYPES


UTC = tzutc()
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

ISO8601 = "ISO8601"
TIMESTAMP = "timestamp"
DEFAULT_PARSE_DATETIME_FORMATS = (ISO8601, TIMESTAMP)


# Subset of Unicode date field patterns from:
# https://www.unicode.org/reports/tr35/tr35-dates.html#Date_Field_Symbol_Table
# that are supported as an alternative to Python's strptime/strftime directives. This mapping is
# used to convert the Unicode pattern (the dict keys) to the best matched strptime directive (the
# values). For values that are tuples, the first item is the directive used for string parsing while
# the second item is the directive used for string formatting. The second items are platform
# dependent and may not work on all systems.
DATE_PATTERN_TO_DIRECTIVE = {
    "yyyy": "%Y",  # Year with century
    "yy": "%y",  # Year without century
    "YYYY": "%Y",  # Year with century
    "YY": "%y",  # Year without century
    "MMMM": "%B",  # Month's full name
    "MMM": "%b",  # Month's abbreviated name
    "MM": "%m",  # Month padded
    "M": "%m",  # Month not padded
    "DDD": "%j",  # Day of the year padded
    "DD": "%j",  # Day of the year padded
    "D": "%j",  # Day of the year not padded
    "dd": "%d",  # Day of the month padded
    "d": "%d",  # Day of the month not padded
    "EEEE": "%A",  # Weekday's full name
    "EEE": "%a",  # Weekday's abbreviated name
    "EE": "%a",  # Weekday's abbreviated name
    "E": "%a",  # Weekday's abbreviated name
    "eee": "%a",  # Weekday's abbreviated name
    "ee": "%w",  # Weekday as decimal padded
    "e": "%w",  # Weekday as decimal not padded
    "HH": "%H",  # Hour-24 padded
    "H": "%H",  # Hour-24 not padded
    "hh": "%I",  # Hour-12 padded
    "h": "%I",  # Hour-12 not padded
    "mm": "%M",  # Minute padded
    "m": "%M",  # Minute not padded
    "ss": "%S",  # Second padded
    "s": "%S",  # Second not padded
    "SSSSSS": "%f",  # Microsecond padded
    "SSSSS": "%f",  # Microsecond padded
    "SSSS": "%f",  # Microsecond padded
    "SSS": "%f",  # Microsecond padded
    "SS": "%f",  # Microsecond padded
    "S": "%f",  # Microsecond not padded
    "a": "%p",  # am or pm
    "z": "%z",  # UTC offset without separator
    "Z": "%z",  # UTC offset without separator
}

TIMEDELTA_GRANULARITIES = ("second", "minute", "hour", "day", "week", "month", "year")

TIMEDELTA_FORMATS = ("long", "short", "narrow")


class ParseError(Exception):
    """Exception raised when an object cannot be parsed as a datetime."""

    pass


def parse_datetime(obj, formats=None, default_tz=None):
    """
    Attempt to parse `obj` as a ``datetime`` using  a list of `formats`. If no timezone information
    is found in `obj` and `default_tz` is set, then the naive datetime object will be shifted to the
    default timezone.

    Args:
        obj (str|datetime): Object to parse.
        formats (str|list, optional): List of string formats to use when parsing. Defaults
            to ``["ISO8601", "X"]``.
        default_tz (None|str|tzinfo, optional): Default timezone to use when parsed
            datetime object does not contain a timezone. Defaults to ``UTC``.

    Returns:
        datetime

    Raises:
        ValueError: When `default_tz` is an unrecognized timezone.
        ParseError: When `obj` can't be parsed as a datetime.
    """
    if default_tz is None:
        default_tz = UTC

    if not is_valid_timezone(default_tz):
        raise ValueError(f"Unrecognized timezone: {default_tz}")

    if is_valid_datetime(obj):
        return obj

    if formats is None:
        formats = DEFAULT_PARSE_DATETIME_FORMATS
    elif not isinstance(formats, (list, tuple)):
        formats = [formats]

    dt = _parse_datetime_formats(obj, formats)

    if dt.tzinfo is None and default_tz is not None:
        dt = dt.replace(tzinfo=get_timezone(default_tz))

    if not has_valid_timezone(dt):  # pragma: no cover
        raise ParseError("Timezone offset must be strictly between -24/+24 " "hours")

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
        err = ", ".join(f'"{format}" ({errors[format]})' for format in formats)
        raise ParseError(f'Value "{obj}" does not match any format in [{err}]')

    return dt


def _parse_datetime_format(obj, format):
    """Parse `obj` as datetime using `format`."""
    if format.upper() == ISO8601:
        return iso8601.parse_date(obj, default_timezone=None)
    elif format.lower() == TIMESTAMP:
        return datetime.fromtimestamp(obj, UTC)
    else:
        if "%" not in format:
            format = _date_pattern_to_directive(format)
        return datetime.strptime(obj, format)


def format_datetime(dt, format=None, tz=None, locale=LC_TIME):
    """
    Return string formatted datetime, `dt`, using format directives or pattern in `format`. If
    timezone, `tz`, is supplied, the datetime will be shifted to that timezone before being
    formatted.

    Args:
        dt (datetime): A datetime instance.
        format (str, optional): Datetime format string. Defaults to ``None`` which uses
            ISO-8601 format.
        tz (None|str|tzinfo, optional): Timezone to shift `dt` to before formatting.
        locale (str|Locale, optional): A ``Locale`` object or locale identifier.
            Defaults to system default.

    Returns:
        str
    """
    if not isinstance(dt, datetime):
        raise TypeError(
            f"zulu.parser.format()'s first argument must be a datetime, not {type(dt).__name__}"
        )  # pragma: no cover

    if format is not None and not isinstance(format, str):
        raise TypeError(
            f"zulu.parser.format()'s second argument must be a string or None,"
            f" not {type(format).__name__}"
        )  # pragma: no cover

    if not is_valid_timezone(tz):  # pragma: no cover
        raise ValueError(f"Unrecognized timezone: {tz}")

    if format is None:
        format = ISO8601

    if tz is not None:
        dt = dt.astimezone(tz)

    if format == ISO8601:
        return dt.isoformat()
    elif "%" in format:
        return dt.strftime(format)
    else:
        # Deviate from TR35 and treat "Y" as "y" when formatting. TR35 defines "Y" as 'Year in
        # "Week of Year" based calendars in which the year transition occurs on a week boundary'.
        # This has caused lots of confusion to users and is honestly not worth sticking with the
        # standard to accommodate.
        # Users should instead use %G, %V and a weekday directive (%A, %a, %w, or %u).
        format = format.replace("Y", "y")
        return _format_datetime(dt, format, locale=locale)


def _date_pattern_to_directive(format):
    """Convert date pattern format to strptime/strftime directives."""
    return "".join(
        DATE_PATTERN_TO_DIRECTIVE.get(token, token) for token in _tokenize_date_pattern(format)
    )


def _tokenize_date_pattern(format):
    """
    Return list of date pattern tokens.

    This groups tokens by repeating characters so that each set of repeating characters is a list
    item (e.g. ``'YY-MM-dd'`` becomes ``['YY', '-', 'MM', '-', 'dd']``).
    """
    return ["".join(group) for key, group in groupby(format)]


def parse_timedelta(obj):
    """
    Attempt to parse `obj` as a ``timedelta`` from a string formatted duration.

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

    is_string = isinstance(obj, str)
    is_number = isinstance(obj, NUMBER_TYPES)

    if not is_string and not is_number:
        raise TypeError(f"Expected string or number type, not {type(obj).__name__}")

    if is_string:
        seconds = pytimeparse.parse(obj)

        if seconds is None:
            raise ParseError(f'Value "{obj}" is not a recognized duration format')
    else:
        seconds = obj

    return timedelta(seconds=seconds)


def format_timedelta(
    delta,
    format="long",
    granularity="second",
    threshold=0.85,
    add_direction=False,
    locale=LC_TIME,
):
    """
    Return timedelta as a formatted string.

    Args:
        format (str, optional): Can be one of "long", "short", or "narrow". Defaults to `"long"`.
        granularity (str, optional): The smallest unit that should be displayed. The value can be
            one of "year", "month", "week", "day", "hour", "minute" or "second". Defaults to
            `"second"`.
        threshold (float, optional): Factor that determines at which point the presentation switches
            to the next higher unit. Defaults to `0.85`.
        add_direction (bool, optional): If ``True`` the return value will include directional
            information (e.g. `'1 hour ago'`, `'in 1 hour'`). Defaults to ``False``.
        locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to system
            default.

    Returns:
        str
    """
    if granularity not in TIMEDELTA_GRANULARITIES:
        units = ", ".join(f'"{unit}"' for unit in TIMEDELTA_GRANULARITIES)
        raise ValueError(f'Time delta granularity must be one of {units}, not "{granularity}"')

    if format not in TIMEDELTA_FORMATS:
        formats = ", ".join(f'"{format}"' for format in TIMEDELTA_FORMATS)
        raise ValueError(f'Time delta format must be one of {formats}, not "{format}"')

    return _format_timedelta(
        delta,
        granularity=granularity,
        threshold=threshold,
        add_direction=add_direction,
        format=format,
        locale=locale,
    )


def get_timezone(tz):
    """
    Coerce `tz` into a `tzinfo` compatible object.

    If ``tz == 'local'``, then the system's local timezone will be used. If `tz` is a string other
    than ``'local'``, it will be passed to ``dateutil.tz.gettz(tz)``. Otherwise, `tz` will be
    returned as-is.
    """
    if tz is None:
        tz = UTC
    elif tz == "local":
        tz = tzlocal()
    elif isinstance(tz, str):
        tz_string = tz
        tz = gettz(tz)

        if tz is None:
            raise ValueError(f"Unrecognized timezone string: {tz_string}")

    return tz


def get_timestamp(dt):
    """Return timestamp for datetime, `dt`."""
    return (dt - EPOCH).total_seconds()


def is_valid_datetime(obj):
    """
    Return whether `obj` is an instance of ``datetime`` or contains date and time attributes.

    Returns:
        bool
    """
    if isinstance(obj, datetime):
        return True
    else:
        attrs = (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "microsecond",
            "tzinfo",
        )
        return all(hasattr(obj, attr) for attr in attrs)


def is_valid_timezone(tz):
    """
    Return whether `tz` is a valid timezone.

    Returns:
        bool
    """
    try:
        get_timezone(tz)
    except Exception:
        return False
    else:
        return True


def has_valid_timezone(dt):
    """
    Return whether `dt` has a valid timezone with a UTC offset strictly between -24/+24 hours.

    Returns:
        bool
    """
    try:
        dt.astimezone(UTC)
    except Exception:  # pragma: no cover
        return False
    else:
        return True
