# -*- coding: utf-8 -*-
"""The api module.
"""

from .datetime import DateTime
from .timedelta import TimeDelta


now = DateTime.now
to_datetime = DateTime.parse
to_timedelta = TimeDelta.parse
