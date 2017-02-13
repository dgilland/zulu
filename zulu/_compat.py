# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""Python 2/3 compatibility

    Some py2/py3 compatibility support based on a stripped down
    version of six so we don't have to depend on a specific version
    of it.

    Borrowed from
    https://github.com/mitsuhiko/flask/blob/master/flask/_compat.py
"""

from decimal import Decimal
from functools import wraps
import sys
import warnings


PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
    number_types = (int, long, float, Decimal)

    def iterkeys(d):
        return d.iterkeys()

    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()
else:
    text_type = str
    string_types = (str,)
    integer_types = (int,)
    number_types = (int, float, Decimal)

    def iterkeys(d):
        return iter(d.keys())

    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())

byte_types = (bytes, bytearray)

def deprecated(func):  # pragma: no cover
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.
    """
    @wraps(func)
    def wrapper(*args, **kargs):
        warnings.warn('Function {0}.{1} has been deprecated and will be '
                      'removed in a future version.'.format(func.__module__,
                                                            func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kargs)
    return wrapper
