# -*- coding: utf-8 -*-
"""The api module.
"""

from .datetime import DateTime
from .parser import format


now = DateTime.now
parse = DateTime.parse
