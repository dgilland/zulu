Changelog
=========


v1.3.0 (2021-01-07)
-------------------

- Add Python 3.9 support.
- Fix bug in ``Zulu.time_from``, ``Zulu.time_to``, ``Zulu.time_from_now``, and ``Zulu.time_to_now`` where keyword arguments weren't passed to underlying ``Delta.format`` call.
- Fix bug in ``Zulu.format`` where "YY" and "YYYY" format patterns would return the year in "Week of Year" based calendars instead of the regular calendar year.


v1.2.0 (2020-01-14)
-------------------

- Add Python 3.8 support.
- Add ``'week'`` option to ``Zulu.start_of``, ``Zulu.end_of``, ``Zulu.span``, and ``Zulu.span_range``. Thanks ThomasChiroux_!
- Fix bug in ``Zulu.astimezone`` in Python 3.8 due to change in return type from ``super().asdatetime``. In Python<=3.7, ``super().asdatetime`` returned as instance of ``datetime``, but in Python 3.8 another instance of ``Zulu`` was returned instead. ``Zulu.astimezone`` will now return a ``datetime`` instance in Python 3.8.


v1.1.1 (2019-08-14)
-------------------

- Remove unused parameter in ``zulu.Timer.__init__()``.


v1.1.0 (2018-11-01)
-------------------

- Add ``fold`` attribute support to ``Zulu``.
- Add ``zulu.to_seconds`` for converting units of time to total number of seconds.
- Add ``zulu.Timer`` class that can be used to track elapsed time (like a stopwatch) or as a countdown timer.


v1.0.0 (2018-08-20)
-------------------

- Drop support for Python 2.7.


v0.12.1 (2018-07-16)
--------------------

- Support Python 3.7.


v0.12.0 (2017-07-11)
--------------------

- Add ``Zulu.datetimetuple()``.
- Add ``Zulu.datetuple()``.
- Remove ``Zulu.__iter__`` method. (**breaking change**)
- Remove ``Delta.__iter__`` method. (**breaking change**)


v0.11.0 (2017-06-28)
--------------------

- Add Python 3.6 support.
- Add ``Delta.__iter__`` method that yields 2-element tuples like ``Zulu.__iter__``. Delta values are normalized into integer values distributed from the higher units to the lower units.
- Add ``Delta.__float__`` and ``Delta.__int__`` methods for converting to seconds.
- Add ``Zulu.__float__`` and ``Zulu.__int__`` methods for converting to epoch seconds.
- Fix issue in Python 3.6 where ``zulu.now()`` returned a naive datetime ``Zulu`` instance.
- Make ``Zulu.__iter__`` yield 2-element tuples containing ``(unit, value)`` like ``(('year', 2000), ('month', 12), ...)`` so it can be converted to a ``dict`` with proper keys easier. (**breaking change**)
- Remove previously deprecated ``zulu.delta()`` function. Use ``zulu.parse_delta()`` instead. (**breaking change**)
- Rename modules: (**breaking change**)

  - ``zulu.datetime -> zulu.zulu``
  - ``zulu.timedelta -> zulu.delta``


v0.10.1 (2017-02-15)
--------------------

- Provide fallback for the default value of ``locale`` in ``Delta.format()`` when a locale is not known via environment variables.


v0.10.0 (2017-02-13)
--------------------

- Add ``zulu.parse_delta`` as alias for ``Delta.parse``.
- Deprecate ``zulu.delta`` in favor of ``zulu.parse_delta``.
- Allow first argument to ``Zulu()``, ``Zulu.parse()``, and ``zulu.parse()`` to be a ``dict`` containing keys corresponding to initialization parameters.
- Fix error message for invalid timezone strings so that the supplied string is shown correctly.


v0.9.0 (2016-11-21)
-------------------

- Require ``python-dateutil>=2.6.0``. (**breaking change**)
- Replace usage of ``pytz`` timezone handling for strings with ``dateutil.tz.gettz``. Continue to support ``pytz`` timezones during ``Zulu()`` object creation. (**breaking change**).
- Replace default UTC timezone with ``dateutil.tz.tzutc()``. Was previously ``pytz.UTC``. (**breaking change**)
- Replace local timezone with ``dateutil.tz.tzlocal()``. Was previously set by the ``tzlocal`` library. (**breaking change**)


v0.8.0 (2016-10-31)
-------------------

- Add comparison methods to ``Zulu``:

  - ``is_before``
  - ``is_on_or_before``
  - ``is_after``
  - ``is_on_or_after``
  - ``is_between``


v0.7.3 (2016-10-24)
-------------------

- Optimize ``Zulu()`` constructor by eliminating multiple unnecessary calls to ``datetime`` constructor.


v0.7.2 (2016-09-06)
-------------------

- Fix ``Zulu`` not being pickle-able.


v0.7.1 (2016-08-22)
-------------------

- Add missing magic method overrides for ``Delta`` for ``+delta``, ``-delta``, and ``abs(delta)`` so that ``Delta`` is returned instead of ``datetime.timedelta``.

  - ``__pos__``
  - ``__neg__``
  - ``__abs__``


v0.7.0 (2016-08-22)
-------------------

- Make ``Zulu.__sub__`` and ``Zulu.subtract`` return a ``Delta`` object instead of ``datetime.timedelta``.
- Make ``zulu.delta`` and ``Zulu.Delta.parse`` accept a number.
- Allow the first argument to ``Zulu.shift`` be a timedelta or relative delta object.
- Ensure that mathematical magic methods for ``Delta`` return ``Delta`` objects and not ``datetime.timedelta``.

  - ``__add__``
  - ``__radd__``
  - ``__sub__``
  - ``__mul__``
  - ``__rmul__``
  - ``__floordiv__``
  - ``__truediv__`` (Python 3 only)
  - ``__div__`` (Python 2 only)
  - ``__mod__`` (Python 3 only)
  - ``__divmod__`` (Python 3 only)


v0.6.0 (2016-08-14)
-------------------

- Replace internal implementation of Unicode date pattern formatting with Babel's ``format_datetime``. **breaking change**
- Remove support for formatting to timestamp using ``X`` and ``XX``. **breaking change**
- Rename parse-from-timestamp token from ``X`` to ``timestamp``. **breaking change**
- Add ``zulu.create`` as factory function to create a ``zulu.Zulu`` instance.
- Add locale support to ``Zulu.format`` when using Unicode date pattern format tokens.
- Restore locale support to ``Delta.format``.


v0.5.0 (2016-08-13)
-------------------

- Remove locale support from ``Delta.format``. Locale is currently not supported in ``Zulu.format`` so decided to disable it in ``Delta.format`` until both can have it. **breaking change**


v0.4.0 (2016-08-13)
-------------------

- Rename ``zulu.DateTime`` to ``zulu.Zulu``. **breaking change**
- Rename ``Zulu.isleap`` to ``Zulu.is_leap_year``. **breaking change**
- Remove ``zulu.format`` alias (function can be accessed at ``zulu.parser.format_datetime``). **breaking change**
- Remove ``Zulu.leapdays``. **breaking change**
- Add ``Zulu.days_in_month``.
- Add ``zulu.Delta`` class that inherits from ``datetime.timedelta``.
- Add ``zulu.delta`` as alias to ``zulu.Delta.parse``.
- Add ``Zulu.time_from``, ``Zulu.time_to``, ``Zulu.time_from_now``, and ``Zulu.time_to_now`` that return "time ago" or "time to" humanized strings.
- Add ``zulu.range`` as alias to ``Zulu.range``.
- Add ``zulu.span_range`` as alias to ``Zulu.span_range``.
- Make time units (years, months, weeks, days, hours, minutes, seconds, microseconds) keyword arguments only for ``Zulu.add/subtract``, but allow positional argument to be an addable/subtractable object (datetime, timedelta, dateutil.relativedelta). **breaking change**


v0.3.0 (2016-08-03)
-------------------

- Rename ``DateTime.sub`` to ``DateTime.subtract``. **breaking change**
- Allow the first argument to ``DateTime.add`` to be a ``datetime.timedelta`` or ``dateutil.relativedelta`` object.
- Allow the first argument to ``DateTime.subtract`` to be a ``DateTime``, ``datetime.datetime``, ``datetime.timedelta``, or ``dateutil.relativedelta`` object.
- Provide ``zulu.ISO8601`` and ``zulu.TIMESTAMP`` as parse/format constants that can be used in ``zulu.parse(string, zulu.ISO8601)`` and ``DateTime.format(zulu.ISO8601)``.
- Remove special parse format string ``'timestamp'`` in favor of using just ``'X'`` as defined in ``zulu.TIMESTAMP``. **breaking change**
- Import ``zulu.parser.format`` to ``zulu.format``.
- Fix bug in ``DateTime`` addition operation that resulted in a native ``datetime`` being returned instead of ``DateTime``.


v0.2.0 (2016-08-02)
-------------------

- Add ``DateTime.datetime`` property that returns a native datetime.
- Add ``DateTime.fromgmtime`` that creates a ``DateTime`` from a UTC based ``time.struct_time``.
- Add ``DateTime.fromlocaltime`` that creates a ``DateTime`` from a local ``time.struct_time``.
- Add ``DateTime.isleap`` method that returns whether its year is a leap year.
- Add ``DateTime.leapdays`` that calculates the number of leap days between its year and another year.
- Add ``DateTime.start_of/end_of`` and other variants that return the start of end of a time frame:

  - ``start/end_of_century``
  - ``start/end_of_decade``
  - ``start/end_of_year``
  - ``start/end_of_month``
  - ``start/end_of_day``
  - ``start/end_of_hour``
  - ``start/end_of_minute``
  - ``start/end_of_second``

- Add ``DateTime.span`` that returns the start and end of a time frame.
- Add ``DateTime.span_range`` that returns a range of spans.
- Add ``DateTime.range`` that returns a range of datetimes.
- Add ``DateTime.add`` and ``DateTime.sub`` methods.
- Add ``years`` and ``months`` arguments to ``DateTime.shift/add/sub``.
- Drop support for milliseconds from ``DateTime.shift/add/sub``. **breaking change**
- Make ``DateTime.parse/format`` understand a subset of `Unicode date patterns <http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table>`_.
- Set defaults for year (1970), month (1), and day (1) arguments to new ``DateTime`` objects. Creating a new ``DateTime`` now defaults to the start of the POSIX epoch.


v0.1.2 (2016-07-26)
-------------------

- Don't pin install requirements to a specific version; use ``>=`` instead.


v0.1.1 (2016-07-26)
-------------------

- Fix bug in ``DateTime.naive`` that resulted in a ``DateTime`` object being returned instead of a native ``datetime``.


v0.1.0 (2016-07-26)
-------------------

- First release.


.. _ThomasChiroux: https://github.com/ThomasChiroux
