# -*- coding: utf-8 -*-
"""The api module.
"""

from .utc import DateTime


def parse(text):
    return DateTime.parse(text)
