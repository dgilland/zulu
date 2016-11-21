Changelog
=========


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
