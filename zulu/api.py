# -*- coding: utf-8 -*-
"""The api module.
"""

from .datetime import Zulu
from .timedelta import Delta


now = Zulu.now
parse = Zulu.parse
range = Zulu.range
span_range = Zulu.span_range
delta = Delta.parse


def create(*args, **kargs):
    """Factory function to create a new :class:`.Zulu` datetime using the same
    arguments as the class.
    """
    return Zulu(*args, **kargs)
