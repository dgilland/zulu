# -*- coding: utf-8 -*-
"""The api module.
"""

from .datetime import Zulu
from .timedelta import Delta
from ._compat import deprecated

now = Zulu.now
parse = Zulu.parse
range = Zulu.range
span_range = Zulu.span_range


def create(*args, **kargs):
    """Factory function to create a new :class:`.Zulu` datetime using the same
    arguments as the class.
    """
    return Zulu(*args, **kargs)


def parse_delta(*args, **kargs):
    """Alias to :meth:`.Delta.parse`.

    .. seealso:: See :meth:`.Delta.parse` for function signature details.
    """
    return Delta.parse(*args, **kargs)


@deprecated
def delta(*args, **kargs):
    """Alias to :meth:`.Delta.parse`.

    .. deprecated:: 0.10.0
       Use :func:`.parse_delta` instead.
    """
    return Delta.parse(*args, **kargs)
