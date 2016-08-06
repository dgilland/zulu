# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datetime import datetime


class Delta(object):
    """Class for retrieving the time delta value in different formats.

    Args:
        start (mixed): Either a :class:`.DateTime`, ``datetime.date``,
            or ``datetime.datetime`` object.
        end (mixed): Either a :class:`.DateTime`, ``datetime.date``,
            or ``datetime.datetime`` object.
        absolute (bool): Boolean value for retrieving an absolute value.
        decimal (bool): A boolean value for retrieving a decimal value.
    """
    def __new__(cls, start, end, absolute=False, decimal=False):
        if not isinstance(start, datetime):
            raise ValueError('{0} should be a valid datetime object'
                             .format(start))

        if not isinstance(end, datetime):
            raise ValueError('{0} should be a valid datetime object'
                             .format(end))

        if start > end and absolute:
            cls.delta_ = start - end
        elif end > start and absolute:
            cls.delta_ = end - start
        elif not absolute:
            cls.delta_ = start - end

        cls.decimal = decimal

        return super(Delta, cls).__new__(cls)

    def delta(self):
        """Returns the original timedelta tuple."""
        return self.delta_

    def total_seconds(self):
        """Retrieve the delta in the seconds."""
        return self.delta_.total_seconds()

    def in_weeks(self):
        """Returns the difference in weeks."""
        weeks = self.total_seconds() / (7 * 24 * 60 * 60)

        return weeks if self.decimal else round(weeks)

    def in_days(self):
        """Returns the difference in days."""
        days = self.total_seconds() / (24 * 60 * 60)

        return days if self.decimal else round(days)

    def in_hours(self):
        """Returns the difference in hours."""
        hours = self.total_seconds() / (60 * 60)

        return hours if self.decimal else round(hours)

    def in_minutes(self):
        """Returns the difference in minutes."""
        minutes = self.total_seconds() / 60

        return minutes if self.decimal else round(minutes)

    def in_seconds(self):
        """Returns the difference in seconds."""
        seconds = self.total_seconds()

        return seconds if self.decimal else round(seconds)

    def in_microseconds(self):
        """Returns the difference in microseconds."""
        microseconds = self.total_seconds() * 1000000

        return microseconds if self.decimal else round(microseconds)
