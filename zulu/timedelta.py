# -*- coding: utf-8 -*-
"""The timedelta module.
"""

from __future__ import absolute_import

from datetime import timedelta

from . import parser


class Delta(timedelta):
    """An extension of ``datetime.timedelta`` that provides additional
    functionality.
    """
    @classmethod
    def parse(cls, obj):
        """Return :class:`.Delta` object parsed from `obj`.

        Args:
            obj (str|timedelta): Object to parse into a :class:`.Delta`
                object.

        Returns:
            :class:`.Delta`
        """
        return cls.fromtimedelta(parser.parse_timedelta(obj))

    @classmethod
    def fromtimedelta(cls, delta):
        """Return :class:`.Delta` object from a native timedelta object.

        Returns:
            :class:`.Delta`
        """
        return cls(seconds=delta.total_seconds())

    def format(self,
               granularity='second',
               threshold=0.85,
               add_direction=False,
               format='long'):
        """Return timedelta as a formatted string.

        Args:
            granularity (str, optional): The smallest unit that should be
                displayed. The value can be one of "year", "month", "week",
                "day", "hour", "minute" or "second". Defaults to `'second'`.
            threshold (float, optional): Factor that determines at which point
                the presentation switches to the next higher unit. Defaults to
                `0.85`.
            add_direction (bool, optional): If ``True`` the return value will
                include directional information (e.g. `'1 hour ago'`,
                `'in 1 hour'`). Defaults to ``False``.
            format (str, optional): Can be one of "long", "short", or "narrow".
                Defaults to `'long`'.
        """
        return parser.format_timedelta(self,
                                       granularity=granularity,
                                       threshold=threshold,
                                       add_direction=add_direction,
                                       format=format)

    def __repr__(self):  # pragma: no cover
        """Return representation of :class:`.Delta`."""
        return '<{0} [{1}]>'.format(self.__class__.__name__, self)
