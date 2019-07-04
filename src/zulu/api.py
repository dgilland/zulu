"""
The api module.
"""

from .zulu import Zulu
from .delta import Delta


def create(*args, **kargs):
    """
    Factory function to create a new :class:`.Zulu` datetime using the same arguments as
    the class.

    .. seealso:: See :class:`.Zulu` for class signature details.
    """
    return Zulu(*args, **kargs)


def now():
    """Alias to :meth:`.Zulu.now`."""
    return Zulu.now()


def parse(*args, **kargs):
    """
    Alias to :meth:`.Zulu.parse`.

    .. seealso:: See :meth:`.Zulu.parse` for function signature details.
    """
    return Zulu.parse(*args, **kargs)


def range(*args, **kargs):
    """
    Alias to :meth:`.Zulu.range`.

    .. seealso:: See :meth:`.Zulu.range` for function signature details.
    """
    return Zulu.range(*args, **kargs)


def span_range(*args, **kargs):
    """
    Alias to :meth:`.Zulu.span_range`.

    .. seealso:: See :meth:`.Zulu.span_range` for function signature details.
    """
    return Zulu.span_range(*args, **kargs)


def parse_delta(*args, **kargs):
    """
    Alias to :meth:`.Delta.parse`.

    .. seealso:: See :meth:`.Delta.parse` for function signature details.
    """
    return Delta.parse(*args, **kargs)
