# -*- coding: utf-8 -*-
"""The api module.
"""

from .datetime import Zulu
from .timedelta import Delta


now = Zulu.now
parse = Zulu.parse
delta = Delta.parse
