"""The zulu module."""

import calendar
from collections import namedtuple
from datetime import datetime, timedelta
import time

from babel.dates import LC_TIME
from dateutil.relativedelta import relativedelta

from . import parser
from .delta import Delta
from .helpers import FOLD_AVAILABLE, NUMBER_TYPES
from .parser import UTC


LOCAL = "local"

DATETIME_ATTRS = (
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "microsecond",
    "tzinfo",
    "fold",
)

TIME_FRAMES = (
    "century",
    "decade",
    "year",
    "month",
    "week",
    "day",
    "hour",
    "minute",
    "second",
)

DateTime = namedtuple(
    "DateTime",
    ["year", "month", "day", "hour", "second", "minute", "microsecond", "tzinfo"],
)
Date = namedtuple("Date", ["year", "month", "day"])


def validate_frame(frame):
    """Method that validates the given time frame."""
    if frame not in TIME_FRAMES:
        raise ValueError(f"Time frame must be one of {'|'.join(TIME_FRAMES)}, not '{frame}'")


class Zulu(datetime):
    """
    The Zulu class represents an immutable UTC datetime object. Any timezone information given to it
    during instantiation results in the datetime object being converted from that timezone to UTC.
    If timezone information is not given, then it's assumed the datetime is a UTC value. All
    arithmetic is perform on the underlying UTC datetime object. Zulu has no concept of timezone
    shifting in this regard. Instead, localization occurs only when formatting a Zulu object as a
    string.

    The Zulu class is a drop-in replacement for a native datetime object, but does not represent
    itself in any time zone other than UTC.

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

    def __new__(
        cls,
        year=1970,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
        *,
        fold=0,
    ):
        if isinstance(year, bytes) and len(year) == 10 and 1 <= year[2] & 0x7F <= 12:
            # Pickle support.
            return cls.fromdatetime(datetime(year, month))
        elif isinstance(year, dict):
            obj = {key: value for key, value in year.items() if key in DATETIME_ATTRS}
            return cls(**obj)

        extra = {"fold": fold} if FOLD_AVAILABLE else {}

        if tzinfo:
            # If tzinfo is provided, we first need to create a stdlib datetime with that
            # tzinfo. Then, we need to convert it to UTC and extract the datetime
            # properites from it so we can then create a Zulu datetime object. We use
            # the stdlib datetime to avoid potential infinite recursion issues if we
            # instead created a Zulu datetime and tried to shift it to UTC.
            tzinfo = parser.get_timezone(tzinfo)

            if hasattr(tzinfo, "localize"):
                # Support pytz timezones.
                dt = tzinfo.localize(
                    datetime(year, month, day, hour, minute, second, microsecond, **extra),
                    is_dst=None,
                )
            else:
                dt = datetime(year, month, day, hour, minute, second, microsecond, tzinfo, **extra)

            if dt.utcoffset() != timedelta(0):
                dt = dt.astimezone(UTC)

            year = dt.year
            month = dt.month
            day = dt.day
            hour = dt.hour
            minute = dt.minute
            second = dt.second
            microsecond = dt.microsecond
            tzinfo = dt.tzinfo

            if FOLD_AVAILABLE:  # pragma: no cover
                extra["fold"] = dt.fold
        else:
            tzinfo = UTC

        return datetime.__new__(
            cls, year, month, day, hour, minute, second, microsecond, tzinfo, **extra
        )

    @classmethod
    def now(cls):
        """
        Return the current UTC date and time as :class:`.Zulu` object.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromtimestamp(time.time())

    @classmethod
    def utcnow(cls):  # pragma: no cover
        """
        Return the current UTC date and time as :class:`.Zulu` object.

        Returns:
            :class:`.Zulu`
        """
        return cls.now()

    @classmethod
    def parse(cls, obj, formats=None, default_tz=None):
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
        if isinstance(obj, dict):
            dt = cls(obj)
        else:
            dt = parser.parse_datetime(obj, formats, default_tz=default_tz)
            dt = cls.fromdatetime(dt)

        return dt

    @classmethod
    def fromdatetime(cls, dt):
        """
        Return :class:`.Zulu` object from a native datetime object.

        Returns:
            :class:`.Zulu`
        """
        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
            fold=getattr(dt, "fold", 0),
        )

    @classmethod
    def fromtimestamp(cls, timestamp, tz=UTC):
        """
        Return :class:`.Zulu` object from a POSIX timestamp.

        Args:
            timestamp (int|float): POSIX timestamp such as is returned by ``time.time()``.
            tz (UTC): This argument is ignored and always set to UTC. It is present only for
                datetime class compatibility.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromdatetime(datetime.fromtimestamp(timestamp, tz))

    @classmethod
    def utcfromtimestamp(cls, timestamp):  # pragma: no cover
        """
        Return :class:`.Zulu` object from a POSIX timestamp.

        Args:
            timestamp (int|float): POSIX timestamp such as is returned by ``time.time()``.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromtimestamp(timestamp)

    @classmethod
    def fromordinal(cls, ordinal):
        """
        Return :class:`.Zulu` object from a proleptic Gregorian ordinal, where January 1 of year 1
        has ordinal 1.

        Args:
            ordinal (int): A proleptic Gregorian ordinal.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromdatetime(datetime.fromordinal(ordinal))

    @classmethod
    def fromgmtime(cls, struct):
        """
        Return :class:`.Zulu` object from a ``tuple`` like that returned by ``time.gmtime`` that
        represents a UTC datetime.

        Args:
            struct (tuple): Tuple like that returned by ``time.gmtime``.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromtimestamp(calendar.timegm(struct))

    @classmethod
    def fromlocaltime(cls, struct):
        """
        Return :class:`.Zulu` object from a ``tuple`` like that returned by ``time.localtime`` that
        represents a local datetime.

        Args:
            struct (tuple): Tuple like that returned by ``time.localtime``.

        Returns:
            :class:`.Zulu`
        """
        return cls.fromtimestamp(time.mktime(struct))

    @classmethod
    def combine(cls, date, time):
        """
        Return :class:`.Zulu` object by combining the date part from `date` and the time part from
        `time`.

        Args:
            date (mixed): Either a :class:`.Zulu`, ``datetime.date``, or ``datetime.datetime``
                object to use as the date part.
            date (mixed): Either a :class:`.Zulu` or ``datetime.time`` object to use as the time
                part.

        Returns:
            :class:`.Zulu`
        """
        if callable(getattr(date, "date", None)):
            date = date.date()

        if callable(getattr(time, "time", None)):
            time = time.time()

        return cls.fromdatetime(datetime.combine(date, time))

    @classmethod
    def span_range(cls, frame, start, end):
        """
        Return a range of time spans from `start` to `end` in steps of time frame, `frame`.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            start (datetime): The starting datetime.
            end (datetime): The ending datetime.

        Yields:
            tuple: 2-element tuple of Zulu time spans
        """
        if not isinstance(start, Zulu):
            start = cls.parse(start)

        if not isinstance(end, Zulu):
            end = cls.parse(end)

        if start > end:
            # Return empty items when start is greater than end.
            return

        # The next starting value to span from.
        next_start = start

        while True:
            # We use the span() method to bring the actual tuple with the given time frame.
            span = next_start.span(frame)

            if span[1] <= end:
                yield span

                # All span-ends have 999999 microseconds set. Shift to the next microsecond to
                # "turn-over" to the next start value of the frame.
                next_start = span[1].shift(microseconds=1)
            else:
                break  # pragma: no cover

    @classmethod
    def range(cls, frame, start, end):
        """
        Yield ranges of :class:`.Zulu` instances from `start` to `end` in steps of time frame,
        `frame`.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            start (datetime): The starting datetime.
            end (datetime): The ending datetime.

        Yields:
            :class:`.Zulu`: Datetime values ranging from the given start and end datetimes.
        """
        if not isinstance(start, Zulu):
            start = cls.parse(start)

        if not isinstance(end, Zulu):
            end = cls.parse(end)

        validate_frame(frame)

        if start > end:
            # Return empty items when start is greater than end.
            return

        if frame == "century":
            # Step every 100 years.
            step_value = 100
            frame = "year"
        elif frame == "decade":
            # Step every 10 years.
            step_value = 10
            frame = "year"
        else:
            # Step every 1 time frame unit.
            step_value = 1

        # Use the plural frame name since the shift() method expects that.
        step = {f"{frame}s": step_value}

        # The next starting value to shift from.
        next_start = start

        while True:
            next_end = next_start.shift(**step)

            if next_end <= end:
                yield next_start
                next_start = next_end
            else:
                break  # pragma: no cover

    @property
    def naive(self):
        """
        The datetime object as a naive datetime (tzinfo=None).

        Note:
            This returns a native datetime object.

        Returns:
            :class:`.Zulu`
        """
        return self.datetime.replace(tzinfo=None)

    @property
    def datetime(self):
        """
        The Zulu object as a native datetime.

        Note:
            This returns a native datetime object.

        Returns:
            :class:`datetime`
        """
        return datetime(*self.datetimetuple())

    def timestamp(self):
        """
        Return the POSIX timestamp.

        Returns:
            :class:`float`
        """
        return parser.get_timestamp(self)

    def datetimetuple(self):
        """
        Return datetime ``tuple`` containing ``(year, month, day, hour, minute, second, microsecond,
        tzinfo)``.

        Returns:
            tuple
        """
        return DateTime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
        )

    def datetuple(self):
        """
        Return date ``tuple`` containing ``(year, month, day)``.

        Returns:
            tuple
        """
        return Date(self.year, self.month, self.day)

    def copy(self):
        """
        Return a new :class`Zulu` instance with the same datetime value.

        Returns:
            :class:`.Zulu`
        """
        return self.__class__(*self.datetimetuple())

    def days_in_month(self):
        """
        Return the number of days in the month.

        Returns:
            int
        """
        return calendar.monthrange(self.year, self.month)[1]

    def format(self, format=None, tz=None, locale=LC_TIME):
        """
        Return datetime as a string using the format string `format` while optionally converting to
        timezone `tz` first.

        Note:
            A ``Locale`` object or string identifier can be provided to display the object in that
            particular locale **but only when using date pattern tokens.** Using a locale other than
            the current system locale is not supported for strftime tokens.

        Args:
            format (str): Format to return string in. If ``None``, ISO 8601 format is used. Defaults
                to ``None``.
            tz (None|str|tzinfo, optional): Timezone to convert to before formatting. Defaults to
                ``None``.
            locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to
                system default.

        Returns:
            str
        """
        return parser.format_datetime(self, format, tz=tz, locale=locale)

    def time_from(
        self,
        dt,
        format="long",
        granularity="second",
        threshold=0.85,
        add_direction=True,
        locale=None,
    ):
        """
        Return "time ago" difference between this datetime and another as a humanized string.

        Args:
            dt (datetime): A datetime object.
            format (str, optional): Can be one of "long", "short", or "narrow". Defaults to
                `"long"`.
            granularity (str, optional): The smallest unit that should be displayed. The value can
                be one of "year", "month", "week", "day", "hour", "minute" or "second". Defaults to
                `"second"`.
            threshold (float, optional): Factor that determines at which point the presentation
                switches to the next higher unit. Defaults to `0.85`.
            add_direction (bool, optional): If ``True`` the return value will include directional
                information (e.g. `'1 hour ago'`, `'in 1 hour'`). Defaults to ``False``.
            locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to
                system default.

        Returns:
            str
        """
        return self._format_delta(
            self - dt,
            format=format,
            granularity=granularity,
            threshold=threshold,
            add_direction=add_direction,
            locale=locale,
        )

    def time_to(
        self,
        dt,
        format="long",
        granularity="second",
        threshold=0.85,
        add_direction=True,
        locale=None,
    ):
        """
        Return "time to" difference between another datetime and this one as a humanized string.

        Args:
            dt (datetime): A datetime object.
            format (str, optional): Can be one of "long", "short", or "narrow". Defaults to
                `"long"`.
            granularity (str, optional): The smallest unit that should be displayed. The value can
                be one of "year", "month", "week", "day", "hour", "minute" or "second". Defaults to
                `"second"`.
            threshold (float, optional): Factor that determines at which point the presentation
                switches to the next higher unit. Defaults to `0.85`.
            add_direction (bool, optional): If ``True`` the return value will include directional
                information (e.g. `'1 hour ago'`, `'in 1 hour'`). Defaults to ``False``.
            locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to
                system default.

        Returns:
            str
        """
        return self._format_delta(
            dt - self,
            format=format,
            granularity=granularity,
            threshold=threshold,
            add_direction=add_direction,
            locale=locale,
        )

    def time_from_now(
        self,
        format="long",
        granularity="second",
        threshold=0.85,
        add_direction=True,
        locale=None,
    ):
        """
        Return "time ago" difference between this datetime and now as a humanized string.

        Args:
            format (str, optional): Can be one of "long", "short", or "narrow". Defaults to
                `"long"`.
            granularity (str, optional): The smallest unit that should be displayed. The value can
                be one of "year", "month", "week", "day", "hour", "minute" or "second". Defaults to
                `"second"`.
            threshold (float, optional): Factor that determines at which point the presentation
                switches to the next higher unit. Defaults to `0.85`.
            add_direction (bool, optional): If ``True`` the return value will include directional
                information (e.g. `'1 hour ago'`, `'in 1 hour'`). Defaults to ``False``.
            locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to
                system default.

        Returns:
            str
        """
        return self.time_from(
            self.now(),
            format=format,
            granularity=granularity,
            threshold=threshold,
            add_direction=add_direction,
            locale=locale,
        )

    def time_to_now(
        self, format="long", granularity="second", threshold=0.85, add_direction=True, locale=None
    ):
        """
        Return "time to" difference between now and this datetime as a humanized string.

        Args:
            format (str, optional): Can be one of "long", "short", or "narrow". Defaults to
                `"long"`.
            granularity (str, optional): The smallest unit that should be displayed. The value can
                be one of "year", "month", "week", "day", "hour", "minute" or "second". Defaults to
                `"second"`.
            threshold (float, optional): Factor that determines at which point the presentation
                switches to the next higher unit. Defaults to `0.85`.
            add_direction (bool, optional): If ``True`` the return value will include directional
                information (e.g. `'1 hour ago'`, `'in 1 hour'`). Defaults to ``False``.
            locale (str|Locale, optional): A ``Locale`` object or locale identifier. Defaults to
                system default.

        Returns:
            str
        """
        return self.time_to(
            self.now(),
            format=format,
            granularity=granularity,
            threshold=threshold,
            add_direction=add_direction,
            locale=locale,
        )

    def _format_delta(self, delta, **options):
        """Return a humanized "time ago"/"time to" string from a timedelta."""
        options.setdefault("add_direction", True)
        delta = Delta(days=delta.days, seconds=delta.seconds, microseconds=delta.microseconds)
        return delta.format(**options)

    def astimezone(self, tz=LOCAL):
        """
        Return datetime shifted to timezone `tz`.

        Note:
            This returns a native datetime object.

        Args:
            tz (None|str|tzinfo, optional): Timezone to shift to. Defaults to `"local"` which uses
                the local timezone.

        Returns:
            :class:`datetime`
        """
        if tz is None:
            tz = LOCAL
        tz = parser.get_timezone(tz)
        return self.datetime.astimezone(tz)

    def shift(
        self,
        other=None,
        years=0,
        months=0,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        microseconds=0,
    ):
        """
        Shift datetime forward or backward using a timedelta created from the supplied arguments and
        return a new :class:`.Zulu` instance.

        Args:
            other (timedelta|relativedelta, optional): A ``timedelta`` or ``dateutil.relativedelta``
                object to add.
            years (int): Years to shift.
            months (int): Months to shift.
            weeks (int): Weeks to shift.
            days (int): Days to shift.
            hours (int): Hours to shift.
            minutes (int): Minutes to shift.
            seconds (int): Seconds to shift.
            microseconds (int): Microseconds to shift.

        Returns:
            :class:`.Zulu`
        """
        if isinstance(other, (timedelta, relativedelta)):
            return self + other

        dt = self + relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )

        return self.fromdatetime(dt)

    def add(
        self,
        other=None,
        years=0,
        months=0,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        microseconds=0,
    ):
        """
        Add time using a timedelta created from the supplied arguments and return a new
        :class:`.Zulu` instance. The first argument can be a `:class:`timedelta` or
        :class:`dateutil.relativedelta` object in which case all other arguments are ignored and the
        object is added to this datetime.

        Args:
            other (timedelta|relativedelta, optional): A ``timedelta`` or ``dateutil.relativedelta``
                object to add.
            years (int): Years to add.
            months (int): Months to add.
            weeks (int): Weeks to add.
            days (int): Days to add.
            hours (int): Hours to add.
            minutes (int): Minutes to add.
            seconds (int): Seconds to add.
            microseconds (int): Microseconds to add.

        Returns:
            :class:`.Zulu`
        """
        if isinstance(other, (timedelta, relativedelta)):
            return self + other

        return self.shift(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )

    def subtract(
        self,
        other=None,
        years=0,
        months=0,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        microseconds=0,
    ):
        """
        Subtract time using a timedelta created from the supplied arguments and return a new
        :class:`.Zulu` instance. The first argument can be a :class:`.Zulu`, :class:`datetime`,
        :class:`timedelta`, or :class:`dateutil.relativedelta` object in which case all other
        arguments are ignored and the object is subtracted from this datetime.

        Args:
            other (datetime|timedelta|relativedelta, optional): A ``datetime``, ``timedelta``, or
                ``dateutil.relativedelta`` object to subtract.
            years (int): Years to subtract.
            months (int): Months to subtract.
            weeks (int): Weeks to subtract.
            days (int): Days to subtract.
            hours (int): Hours to subtract.
            minutes (int): Minutes to subtract.
            seconds (int): Seconds to subtract.
            microseconds (int): Microseconds to subtract.

        Returns:
            :class:`.Zulu`: if subtracting :class:`timedelta` or :class:`timedelta`.
            :class:`timedelta`: if subtracting a :class:`datetime` or :class:`.Zulu`.
        """
        if isinstance(other, (datetime, timedelta, relativedelta)):
            return self - other

        return self.shift(
            years=-years,
            months=-months,
            weeks=-weeks,
            days=-days,
            hours=-hours,
            minutes=-minutes,
            seconds=-seconds,
            microseconds=-microseconds,
        )

    def replace(
        self,
        year=None,
        month=None,
        day=None,
        hour=None,
        minute=None,
        second=None,
        microsecond=None,
        tzinfo=None,
        *,
        fold=None,
    ):
        """
        Replace datetime attributes and return a new :class:`.Zulu` instance.

        Args:
            year (None|int, optional): Year to replace.
            month (None|int, optional): Month to replace.
            week (None|int, optional): Week to replace.
            day (None|int, optional): Day to replace.
            hour (None|int, optional): Hour to replace.
            minute (None|int, optional): Minute to replace.
            second (None|int, optional): Second to replace.
            microsecond (None|int, optional): Microsecond to replace.
            tzinfo (None|str|tzinfo, optional): Timezone to replace.
            fold (None|int, optional): Fold to replace.

        Returns:
            :class:`.Zulu`
        """
        dt = self.datetimetuple()
        values = [year, month, day, hour, minute, second, microsecond, tzinfo]

        for idx, value in enumerate(values):
            if value is None:
                values[idx] = dt[idx]

        if fold is None:
            fold = getattr(self, "fold", 0)

        return self.__class__(*values, fold=fold)

    def start_of_century(self):
        """
        Return a new :class:`.Zulu` set to the start of the century of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(
            year=self.year - (self.year % 100),
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    def start_of_decade(self):
        """
        Return a new :class:`.Zulu` set to the start of the decade of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(
            year=self.year - (self.year % 10),
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    def start_of_year(self):
        """
        Return a new :class:`.Zulu` set to the start of the year of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    def start_of_month(self):
        """
        Return a new :class:`.Zulu` set to the start of the month of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def start_of_week(self):
        """
        Return a new :class:`.Zulu` set to the start of the week of this datetime. uses ISO8601
        definition of week: week start is monday.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(hour=0, minute=0, second=0, microsecond=0).shift(
            days=-self.isoweekday() + 1
        )

    def start_of_day(self):
        """
        Return a new :class:`.Zulu` set to the start of the day of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(hour=0, minute=0, second=0, microsecond=0)

    def start_of_hour(self):
        """
        Return a new :class:`.Zulu` set to the start of the hour of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(minute=0, second=0, microsecond=0)

    def start_of_minute(self):
        """
        Return a new :class:`.Zulu` set to the start of the minute of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(second=0, microsecond=0)

    def start_of_second(self):
        """
        Return a new :class:`.Zulu` set to the start of the second of this datetime.

        Returns:
            :class:`.Zulu`
        """
        return self.replace(microsecond=0)

    def end_of_century(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the century of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_century().shift(years=count * 100, microseconds=-1)

    def end_of_decade(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the decade of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_decade().shift(years=count * 10, microseconds=-1)

    def end_of_year(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the year of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_year().shift(years=count, microseconds=-1)

    def end_of_month(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the month of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_month().shift(months=count, microseconds=-1)

    def end_of_week(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the week of this datetime. uses ISO8601
        definition of week: week start is monday.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_week().shift(weeks=count, microseconds=-1)

    def end_of_day(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the day of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_day().shift(days=count, microseconds=-1)

    def end_of_hour(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the hour of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_hour().shift(hours=count, microseconds=-1)

    def end_of_minute(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the minute of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_minute().shift(minutes=count, microseconds=-1)

    def end_of_second(self, count=1):
        """
        Return a new :class:`.Zulu` set to the end of the second of this datetime.

        Args:
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        return self.start_of_second().shift(seconds=count, microseconds=-1)

    def start_of(self, frame):
        """
        Return the start of the given time frame for this datetime.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).

        Returns:
            :class:`.Zulu`
        """
        validate_frame(frame)
        return getattr(self, f"start_of_{frame}")()

    def end_of(self, frame, count=1):
        """
        Return the end of a given time frame for this datetime.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            count (int): Number of frames to span.

        Returns:
            :class:`.Zulu`
        """
        validate_frame(frame)
        return getattr(self, f"end_of_{frame}")(count)

    def span(self, frame, count=1):
        """
        Returns two new :class:`.Zulu` objects corresponding to the time span between this object
        and the given time frame.

        Args:
            frame (str): A time frame (e.g. year, month, day, minute, etc).
            count (int): Number of frames to span.

        Returns:
            tuple: (`start_of_frame`, `end_of_frame`)
        """
        return self.start_of(frame), self.end_of(frame, count)

    def is_leap_year(self):
        """
        Return whether this datetime's :attr:`year` is a leap year.

        Returns:
            bool
        """
        return calendar.isleap(self.year)

    def is_before(self, other):
        """
        Return whether this datetime is before `other`.

        Args:
            other (datetime): Other datetime to compare.

        Returns:
            bool
        """
        return self < other

    def is_on_or_before(self, other):
        """
        Return whether this datetime is before or on `other`.

        Args:
            other (datetime): Other datetime to compare.

        Returns:
            bool
        """
        return self <= other

    def is_after(self, other):
        """
        Return whether this datetime is after `other`.

        Args:
            other (datetime): Other datetime to compare.

        Returns:
            bool
        """
        return self > other

    def is_on_or_after(self, other):
        """
        Return whether this datetime is after or on `other`.

        Args:
            other (datetime): Other datetime to compare.

        Returns:
            bool
        """
        return self >= other

    def is_between(self, start, end):
        """
        Return whether this datetime is between `start` and `end` inclusively.

        Args:
            start (datetime): Starting datetime to compare.
            end (datetime): Ending datetime to compare.

        Returns:
            bool
        """
        return start <= self <= end

    def __repr__(self):  # pragma: no cover
        """Return representation of :class:`.Zulu`."""
        return f"<{self.__class__.__name__} [{self}]>"

    def __str__(self):
        """Return class as an ISO8601 string."""
        return self.isoformat()

    def __float__(self):
        """Return class as float time in seconds (including decimal microsceonds) since the
        epoch."""
        return (self - self.epoch).total_seconds()

    def __int__(self):
        """Return class as integer time in seconds since the epoch."""
        return int(float(self))

    def __add__(self, other):
        """
        Add a ``timedelta`` and return the result.

        Returns:
            :class:`.Zulu`
        """
        if not isinstance(other, (timedelta, relativedelta, NUMBER_TYPES)):
            return NotImplemented

        if isinstance(other, NUMBER_TYPES):
            other = timedelta(seconds=other)

        if isinstance(other, timedelta):
            result = super().__add__(other)
        else:
            result = other.__add__(self)

        return self.fromdatetime(result)

    __radd__ = __add__

    def __sub__(self, other):
        """
        Subtract a ``timedelta``, ``dateutil.relativedelta``, ``datetime``, or :class:`.Zulu` and
        return the result.

        Returns:
            :class:`.Zulu`: if subtracting a :class:`timedelta`
            :class:`timedelta`: if subtracting a :class:`datetime` or :class:`.Zulu`
        """
        if not isinstance(other, Zulu) and isinstance(other, datetime):
            other = self.fromdatetime(other)

        result = super().__sub__(other)

        if isinstance(result, datetime):
            return self.fromdatetime(result)
        elif isinstance(result, timedelta):
            return Delta.fromtimedelta(result)
        else:
            return result


#: Minimum Zulu value.
Zulu.min = Zulu(1, 1, 1)

#: Maximum Zulu value.
Zulu.max = Zulu(9999, 12, 31, 23, 59, 59, 999999)

#: Zulu value of EPOCH.
Zulu.epoch = Zulu.fromdatetime(parser.EPOCH)
