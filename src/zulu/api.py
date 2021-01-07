"""The api module."""

from .delta import Delta
from .zulu import Zulu


def create(
    year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0
):
    """
    Factory function to create a new :class:`.Zulu` datetime using the same arguments as the class.

    Args:
        year (int|dict): Date year ``1 <= year <= 9999`` or ``dict`` containing keys corresponding
            to initialization parameter names.
        month (int): Date month ``1 <= month <= 12``.
        day (int): Date day ``1 <= day <= number of days in the given month and year``
        hour (int, optional): Time hour ``0 <= hour < 24``. Defaults to ``0``.
        minute (int, optional): Time minute ``0 <= minute < 60``. Defaults to ``0``.
        second (int, optional): Time second ``0 <= second < 60``. Defaults to ``0``.
        microsecond (int, optional): Time microsecond ``0 <= microsecond < 1000000``. Defaults to
            ``0``.
        tzinfo (None|str|tzinfo, optional): Timezone information as either a ``str`` or ``tzinfo``
            subclass. If value is a ``str``, it will be converted to a ``dateutil.tz`` timezone. If
            value is ``None``, the datetime values given are assumed to in UTC. Defaults to
            ``None``.
    """
    return Zulu(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
        tzinfo=tzinfo,
        fold=fold,
    )


def now():
    """Alias to :meth:`.Zulu.now`."""
    return Zulu.now()


def parse(obj, formats=None, default_tz=None):
    """
    Return :class:`.Zulu` object parsed from `obj`.

    Args:
        obj (mixed): Object to parse into a :class:`.Zulu` object.
        formats (str|list, optional): List of string formats to use when parsing. Defaults to
            ``["ISO8601", "timestamp"]``.
        default_tz (None|str|tzinfo, optional): Default timezone to use when parsed datetime
            object does not contain a timezone. Defaults to ``UTC``.

    Returns:
        :class:`.Zulu`
    """
    return Zulu.parse(obj, formats=formats, default_tz=default_tz)


def range(frame, start, end):
    """
    Yield ranges of :class:`.Zulu` instances from `start` to `end` in steps of time frame, `frame`.

    Args:
        frame (str): A time frame (e.g. year, month, day, minute, etc).
        start (datetime): The starting datetime.
        end (datetime): The ending datetime.

    Yields:
        :class:`.Zulu`: Datetime values ranging from the given start and end datetimes.
    """
    yield from Zulu.range(frame, start, end)


def span_range(frame, start, end):
    """
    Return a range of time spans from `start` to `end` in steps of time frame, `frame`.

    Args:
        frame (str): A time frame (e.g. year, month, day, minute, etc).
        start (datetime): The starting datetime.
        end (datetime): The ending datetime.

    Yields:
        tuple: 2-element tuple of Zulu time spans
    """
    yield from Zulu.span_range(frame, start, end)


def parse_delta(obj):
    """
    Return :class:`.Delta` object parsed from `obj`.

    Args:
        obj (str|number|timedelta): Object to parse into a :class:`.Delta` object.

    Returns:
        :class:`.Delta`
    """
    return Delta.parse(obj)
