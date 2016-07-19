# -*- coding: utf-8 -*-
"""The api module.
"""

from datetime import datetime

from .datetime import DateTime


def parse(text):
    return DateTime.parse(text)
