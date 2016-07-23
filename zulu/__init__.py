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


from .api import now, parse
from .utc import DateTime
from .parser import ParseError
