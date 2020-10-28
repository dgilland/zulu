"""The timedelta module."""

from datetime import timedelta
from functools import wraps

from babel.core import default_locale

from . import parser


def _asdelta(func):
    """
    Simple decorator to convert return from timedelta.__<math>__ methods to Delta object. This is
    primarily needed because one cannot simply override the existing timedelta method due to the way
    the class is implemented. Doing so results in slotted attributes not being available to the
    subclassed methods. Therefore, we need to convert the returned timedelta to Delta instead.

    Note:
        We could reimplement all of the arithmetic magic methods but prefer not to. However, we do
        end up creating timedelta objects twice (one from the timedelta result, another when we
        create a new Delta) so there would be some performance gains from doing so though.
    """
    # NOTE: We're setting assigned because in Python 2.7, @wraps fails for certain timedelta magic
    # methods due to certain attributes missing from the timedelta class that @wraps looks for by
    # default.
    @wraps(func, assigned=("__name__", "__doc__"))
    def decorated(*args, **kargs):
        result = func(*args, **kargs)

        if isinstance(result, timedelta):
            return Delta.fromtimedelta(result)
        elif isinstance(result, tuple):  # pragma: no cover
            # This handles __divmod__ return.
            return tuple(
                Delta.fromtimedelta(item) if isinstance(item, timedelta) else item
                for item in result
            )
        else:  # pragma: no cover
            return result

    return decorated


def get_locale(locale=None, default="en_US_POSIX"):
    """Return default locale to use if one is not provided."""
    if not locale:
        locale = default_locale("LC_TIME")

        if not locale:
            locale = default

    return locale


class Delta(timedelta):
    """An extension of ``datetime.timedelta`` that provides additional functionality."""

    @classmethod
    def parse(cls, obj):
        """
        Return :class:`.Delta` object parsed from `obj`.

        Args:
            obj (str|number|timedelta): Object to parse into a :class:`.Delta` object.

        Returns:
            :class:`.Delta`
        """
        return cls.fromtimedelta(parser.parse_timedelta(obj))

    @classmethod
    def fromtimedelta(cls, delta):
        """
        Return :class:`.Delta` object from a native timedelta object.

        Returns:
            :class:`.Delta`
        """
        return cls(seconds=delta.total_seconds())

    def format(
        self,
        format="long",
        granularity="second",
        threshold=0.85,
        add_direction=False,
        locale=None,
    ):
        """
        Return timedelta as a formatted string.

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
        return parser.format_timedelta(
            self,
            format=format,
            granularity=granularity,
            threshold=threshold,
            add_direction=add_direction,
            locale=get_locale(locale),
        )

    def __float__(self):
        """Return class as float which returns the same as :meth:`total_seconds`."""
        return self.total_seconds()

    def __int__(self):
        """Return class as integer which returns the integer part of
        :meth:`total_seconds`."""
        return int(float(self))

    def __repr__(self):  # pragma: no cover
        """Return representation of :class:`.Delta`."""
        return "<{0} [{1}]>".format(self.__class__.__name__, self)


# See _asdelta() docstring for details on why we are doing this.
Delta.__add__ = _asdelta(Delta.__add__)
Delta.__radd__ = _asdelta(Delta.__radd__)
Delta.__sub__ = _asdelta(Delta.__sub__)
Delta.__mul__ = _asdelta(Delta.__mul__)
Delta.__rmul__ = _asdelta(Delta.__rmul__)
Delta.__floordiv__ = _asdelta(Delta.__floordiv__)
Delta.__pos__ = _asdelta(Delta.__pos__)
Delta.__neg__ = _asdelta(Delta.__neg__)
Delta.__abs__ = _asdelta(Delta.__abs__)
Delta.__truediv__ = _asdelta(Delta.__truediv__)
Delta.__mod__ = _asdelta(Delta.__mod__)
Delta.__divmod__ = _asdelta(Delta.__divmod__)
# Override timedelta.min/max/resolution with equivalent Delta objects.
Delta.min = Delta(-999999999)
Delta.max = Delta(days=999999999, hours=23, minutes=59, seconds=59, microseconds=999999)
Delta.resolution = Delta(microseconds=1)


def to_seconds(*, microseconds=0, milliseconds=0, seconds=0, minutes=0, hours=0, days=0, weeks=0):
    """Return total number of seconds by combining values from each unit."""
    return Delta(
        microseconds=microseconds,
        milliseconds=milliseconds,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        days=days,
        weeks=weeks,
    ).total_seconds()
