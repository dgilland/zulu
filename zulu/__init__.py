# -*- coding: utf-8 -*-
"""The zulu module.
"""

from .__pkg__ import (
    __description__,
    __url__,
    __version__,
    __author__,
    __email__,
    __license__
)


from .api import (
    create,
    delta,
    now,
    parse,
    parse_delta,
    range,
    span_range
)
from .datetime import Zulu
from .parser import ParseError, ISO8601, TIMESTAMP
from .timedelta import Delta
