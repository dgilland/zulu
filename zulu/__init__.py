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


from .api import format, now, parse
from .datetime import DateTime
from .parser import ParseError, ISO8601, TIMESTAMP
from .timedelta import TimeDelta
