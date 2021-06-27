"""The zulu library."""

__version__ = "1.3.1"

from .api import create, now, parse, parse_delta, range, span_range
from .delta import Delta, to_seconds
from .parser import ISO8601, TIMESTAMP, ParseError
from .timer import Timer
from .zulu import Zulu
