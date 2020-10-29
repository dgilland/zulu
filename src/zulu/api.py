"""The api module."""

from .delta import Delta
from .zulu import Zulu


def create(*args, **kwargs):
    """
    Factory function to create a new :class:`.Zulu` datetime using the same arguments as the class.

    .. seealso:: See :class:`.Zulu` for class signature details.
    """
    return Zulu(*args, **kwargs)


def now():
    """Alias to :meth:`.Zulu.now`."""
    return Zulu.now()


def parse(*args, **kwargs):
    """
    Alias to :meth:`.Zulu.parse`.

    .. seealso:: See :meth:`.Zulu.parse` for function signature details.
    """
    return Zulu.parse(*args, **kwargs)


def range(*args, **kwargs):
    """
    Alias to :meth:`.Zulu.range`.

    .. seealso:: See :meth:`.Zulu.range` for function signature details.
    """
    return Zulu.range(*args, **kwargs)


def span_range(*args, **kwargs):
    """
    Alias to :meth:`.Zulu.span_range`.

    .. seealso:: See :meth:`.Zulu.span_range` for function signature details.
    """
    return Zulu.span_range(*args, **kwargs)


def parse_delta(*args, **kwargs):
    """
    Alias to :meth:`.Delta.parse`.

    .. seealso:: See :meth:`.Delta.parse` for function signature details.
    """
    return Delta.parse(*args, **kwargs)
