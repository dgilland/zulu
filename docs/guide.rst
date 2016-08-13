User's Guide
============

Zulu's main type is ``zulu.Zulu`` which represents a fixed UTC datetime object.

.. code-block:: python

    import zulu

    dt = zulu.parse('2016-07-25T19:33:18.137493+00:00')
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    assert isinstance(dt, zulu.Zulu)

    from datetime import datetime
    assert isinstance(dt, datetime)


It's a drop-in replacement for native datetime objects (it inherits from ``datetime.datetime``) but deals only with UTC time zones internally.


Basic Data Access
-----------------

All the attributes and methods from `datetime <https://docs.python.org/3.5/library/datetime.html>`_ are available along with a few new ones:

.. code-block:: python

    assert dt.year == 2016
    assert dt.month == 7
    assert dt.day == 25
    assert dt.hour == 19
    assert dt.minute == 33
    assert dt.second == 18
    assert dt.microsecond == 137493
    assert dt.tzname() == 'UTC'

    dt.utcoffset()
    # datetime.timedelta(0)

    dt.dst()
    # datetime.timedelta(0)

    dt.isoformat()
    # '2016-07-25T19:33:18.137493+00:00'

    dt.weekday()
    # 0

    dt.isoweekday()
    # 1

    dt.isocalendar()
    # (2016, 30, 1)

    dt.ctime()
    # 'Mon Jul 25 19:33:18 2016'

    dt.toordinal()
    # 736170

    dt.timetuple()
    # time.struct_time(tm_year=2016, tm_mon=7, tm_mday=25, tm_hour=19, tm_min=33, tm_sec=18,
    #                  tm_wday=0, tm_yday=207, tm_isdst=0)

    dt.utctimetuple()
    # time.struct_time(tm_year=2016, tm_mon=7, tm_mday=25, tm_hour=19, tm_min=33, tm_sec=18,
    #                  tm_wday=0, tm_yday=207, tm_isdst=0)

    dt.timestamp()
    # 1469475198.137493

    dt.date()
    # datetime.date(2016, 7, 25)

    dt.time()
    # datetime.time(19, 33, 18, 137493)

    dt.timetz()
    # datetime.time(19, 33, 18, 137493, tzinfo=<UTC>)


Along with a few new ones:

.. code-block:: python

    dt.naive
    # datetime.datetime(2016, 7, 25, 19, 33, 18, 137493)

    dt.datetime
    # datetime.datetime(2016, 7, 25, 19, 33, 18, 137493, tzinfo=<UTC>)

    dt.is_leap_year()
    # True

    dt.days_in_month()
    # 31

    tuple(dt)
    # (2016, 7, 25, 19, 33, 18, 137493, <UTC>)


Parsing and Formatting
----------------------

By default, ``zulu.parse`` will look for either an ISO8601 formatted string or a POSIX timestamp while assuming a UTC timezone when no explicit timezone found in the string:

.. code-block:: python

    zulu.parse('2016-07-25 15:33:18-0400')
    # <Zulu [2016-07-25T19:33:18+00:00]>

    zulu.parse('2016-07-25 15:33:18-0400', zulu.ISO8601)
    # <Zulu [2016-07-25T19:33:18+00:00]>

    zulu.parse('2016-07-25')
    # <Zulu [2016-07-25T00:00:00+00:00]>

    zulu.parse('2016-07-25 19:33')
    # <Zulu [2016-07-25T19:33:00+00:00]>

    zulu.parse(1469475198.0)
    # <Zulu [2016-07-25T19:33:18+00:00]>

    zulu.parse(1469475198.0, zulu.TIMESTAMP)
    # <Zulu [2016-07-25T19:33:18+00:00]>


Multiple formats can be supplied and ``zulu.parse`` will try them all:

.. code-block:: python

    zulu.parse('3/2/1992', 'ISO8601')
    # zulu.parser.ParseError: Value "3/2/1992" does not match any format in "ISO8601"
    # (Unable to parse date string '3/2/1992')

    dt = zulu.parse('3/2/1992', ['ISO8601', 'MM/dd/YYYY'])
    # <Zulu [1992-03-02T00:00:00+00:00]>


As shown above, special parse format keywords are supported. See `Keyword Parse Formats`_ for details.

Other time zones can be substituted for naive datetimes by setting ``default_tz``:

.. code-block:: python

    zulu.parse('2016-07-25', default_tz='US/Eastern')
    # <Zulu [2016-07-25T04:00:00+00:00]>

    zulu.parse('2016-07-25', default_tz='local')
    # <Zulu [2016-07-25T04:00:00+00:00]>


The default timezone is ignored when the input has it set:

.. code-block:: python

    zulu.parse('2016-07-25T15:33:18-0700', default_tz='US/Eastern')
    # <Zulu [2016-07-25T22:33:18+00:00]>


String parsing/formatting in ``Zulu`` supports both `strftime/strptime <https://docs.python.org/3.5/library/datetime.html#strftime-and-strptime-behavior>`_ directives and `Unicode date patterns <http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table>`_.

.. code-block:: python

    dt.format('%Y-%m-%d %H:%M:%S%z')
    # '2016-07-25 19:33:18+0000'

    dt.format('YYYY-MM-dd HH:mm:ssZ')
    # '2016-07-25 19:33:18+0000'

    dt.format('%Y-%m-%d %H:%M:%S%z', tz='US/Eastern')
    # '2016-07-25 15:33:18-0400'

    dt.format('%Y-%m-%d %H:%M:%S%z', tz='local')
    # '2016-07-25 15:33:18-0400'

    zulu.parse('2016-07-25 15:33:18-0400', '%Y-%m-%d %H:%M:%S%z')
    # <Zulu [2016-07-25T19:33:18+00:00]>


You can even use ``zulu.parser.format_datetime`` with native datetimes:

.. code-block:: python

    from zulu.parser import format_datetime

    native = datetime(2016, 7, 25, 19, 33, 18, 137493, tzinfo=pytz.UTC)

    format_datetime(native, '%Y-%m-%d %H:%M:%S%z')
    # '2016-07-25 19:33:18+0000'

    format_datetime(native, 'YYYY-MM-dd HH:mm:ssZ')
    # '2016-07-25 19:33:18+0000'

    dt = Zulu.fromdatetime(native)
    format_datetime(dt, 'YYYY-MM-dd HH:mm:ssZ')
    # '2016-07-25 19:33:18+0000'


Keyword Parse Formats
+++++++++++++++++++++

The following keywords can be supplied to ``zulu.parse`` in place of a format directive or pattern:

.. code-block:: python

    zulu.parse(1469475198, 'X')
    # <Zulu [2016-07-25T19:33:18+00:00]>


========== ========================= ===========================
Keyword    Description               Sample Input
========== ========================= ===========================
ISO8601    Parse ISO8601 string      - 2016-07-25 15:33:18-0400
                                     - 2016-07-25 15:33
                                     - 2016-07-25
                                     - 2016-07
X          Parse POSIX timestamp     - 1469475198
                                     - 1469475198.314218
========== ========================= ===========================


Format Tokens
-------------

Zulu supports two different styles of string parsing/formatting tokens:

- All `Python strptime/strftime directives <https://docs.python.org/3.5/library/datetime.html#strftime-and-strptime-behavior>`_
- A subset of `Unicode date patterns <http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table>`_

Either style can be used during parsing:

.. code-block:: python

    dt = zulu.parse('07/25/16 15:33:18 -0400', '%m/%d/%y %H:%M:%S %z')
    # <Zulu [2016-07-25T19:33:18+00:00]>

    dt = zulu.parse('07/25/16 15:33:18 -0400', 'MM/dd/YY HH:mm:ss Z')
    # <Zulu [2016-07-25T19:33:18+00:0


and formatting:

.. code-block:: python

    dt.format('%m/%d/%y %H:%M:%S %z')
    # '07/25/16 19:33:18 +0000'

    dt.format('MM/dd/YY HH:mm:ss Z')
    '07/25/16 19:33:18 +0000'


Format Directives
+++++++++++++++++

All directives from https://docs.python.org/3.5/library/datetime.html#strftime-and-strptime-behavior are supported.


Date Patterns
+++++++++++++

A subset of patterns from http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table are supported:

============= ================ ======== =============================================
Attribute     Style            Pattern  Sample Output
============= ================ ======== =============================================
Year          4-digit          YYYY     2000, 2001, 2002 ... 2015, 2016
Year          2-digit          YY       00, 01, 02 ... 15, 16
Month         full name        MMMM     January, February, March
Month         abbr name        MMM      Jan, Feb, Mar ... Nov, Dec
Month         int, padded      MM       01, 02, 03 ... 11, 12
Month         int, no padding  M        1, 2, 3 ... 11, 12
Day of Month  int, padded      dd       01, 02, 03 ... 30, 31
Day of Month  int, no padding  d        1, 2, 3 ... 30, 31
Day of Year   int, padded      DDD      001, 002, 003 ... 054, 055 ... 364, 365
Day of Year   int, padded      DD       01, 02, 03 ... 54, 55 ... 364, 365
Day of Year   int, no padding  D        1, 2, 3 ... 54, 55 ... 364, 365
Weekday       full name        EEEE     Monday, Tuesday, Wednesday
Weekday       abbr name        EEE      Mon, Tue, Wed
Weekday       abbr name        EE       Mon, Tue, Wed
Weekday       abbr name        E        Mon, Tue, Wed
Weekday       abbr name        eee      Mon, Tue, Wed
Weekday       int, padded      ee       01, 02, 03 ... 06, 07
Weekday       int, no padding  e        1, 2, 3 ... 6, 7
Hour          24h, padded      HH       00, 01, 02 ... 22, 23
Hour          24h, no padding  H        0, 1, 2 ... 22, 23
Hour          12h, padded      hh       00, 01, 02 ... 11, 12
Hour          12h, no padding  h        0, 1, 2, ... 11, 12
AM / PM       upper case       A        AM, PM
AM / PM       lower case       a        am, pm
Minute        int, padded      mm       00, 01, 02 ... 58, 59
Minute        int, no padding  m        0, 1, 2 ... 58, 59
Second        int, padded      ss       00, 01, 02 ... 58, 59
Second        int, no padding  s        0, 1, 2 ... 58, 59
Microsecond   int, padded      SSSSSS   000000, 000001 ... 999998, 999999
Microsecond   int, truncated   SSSSS    00000, 00001 ... 99998, 99999
Microsecond   int, truncated   SSSS     0000, 0001 ... 9998, 9999
Microsecond   int, truncated   SSS      000, 001 ... 998, 999
Microsecond   int, truncated   SS       00, 01 ... 98, 99
Microsecond   int, truncated   S        0, 1 ... 8, 9
Timezone      w/o separator    Z        -1100, -1000 ... +0000 ... +1100, +1200
Timezone      w/ separator     ZZ       -11:00, -10:00 ... +00:00 ... +11:00, +12:00
Timestamp     float            XX       1470111298.690562
Timestamp     int              X        1470111298
============= ================ ======== =============================================


Humanization
++++++++++++

You can humanize the difference between two ``Zulu`` objects with ``Zulu.time_from`` and ``Zulu.time_to``:


.. code-block:: python

    dt
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    dt.time_from(dt.end_of_day())
    # '4 hours ago'

    dt.time_to(dt.end_of_day())
    # 'in 4 hours'

    dt.time_from(dt.start_of_day())
    # 'in 20 hours'

    dt.time_to(dt.start_of_day())
    # '20 hours ago'

    zulu.now()
    # <Zulu [2016-08-12T04:16:17.007335+00:00]>

    dt.time_from_now()
    # 2 weeks ago

    dt.time_to_now()
    # in 2 weeks


Time Zone Handling
------------------

Time zones other than UTC are not expressable within a ``Zulu`` instance. Other time zones are only ever applied when either converting a ``Zulu`` object to a native datetime (via ``Zulu.astimezone``) or during string formatting (via ``Zulu.format``). ``Zulu`` understands both ``tzinfo`` objects and ``pytz.timezone`` string names.


.. code-block:: python

    local = dt.astimezone()
    # same as doing dt.astimezone('local')
    # datetime.datetime(2016, 7, 25, 15, 33, 18, 137493,
    #                   tzinfo=<DstTzInfo 'America/New_York' EDT-1 day, 20:00:00 DST>)

    pacific = dt.astimezone('US/Pacific')
    # datetime.datetime(2016, 7, 25, 12, 33, 18, 137493,
    #                   tzinfo=<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>)

    import pytz
    mountain = dt.astimezone(pytz.timezone('US/Mountain'))
    # datetime.datetime(2016, 7, 25, 13, 33, 18, 137493,
    #                   tzinfo=<DstTzInfo 'US/Mountain' MDT-1 day, 18:00:00 DST>)


Shifting, Replacing, and Copying
--------------------------------

Zulu can easily apply timedelta's using the ``shift`` method:

.. code-block:: python

    shifted = dt.shift(hours=-5, minutes=10)
    # <Zulu [2016-07-25T14:43:18.137493+00:00]>

    assert shifted is not dt


And add and subtract with the ``add`` and ``subtract`` methods:

.. code-block:: python

    shifted = dt.subtract(hours=5).add(minutes=10)
    # <Zulu [2016-07-25T14:43:18.137493+00:00]>

    # First argument to subtract() can be a timedelta or dateutil.relativedelta
    shifted = dt.subtract(timedelta(hours=5))
    # <Zulu [2016-07-25T14:33:18+00:00]>

    # First argument to subtract() can also be another datetime object
    dt.subtract(shifted)
    # datetime.timedelta(0, 18000)

    # First argument to add() can be a timedelta or dateutil.relativedelta
    dt.add(timedelta(minutes=10))
    # <Zulu [2016-07-25T19:43:18+00:00]>


Or replace datetime attributes:

.. code-block:: python

    replaced = dt.replace(hour=14, minute=43)
    # <Zulu [2016-07-25T14:43:18.137493+00:00]>

    assert replaced is not dt


Or even make a copy:

.. code-block:: python

    copied = dt.copy()
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    assert copied is not dt
    assert copied == dt


.. note:: Since ``Zulu`` is meant to be immutable, both ``shift``, ``replace``, and ``copy`` return new ``Zulu`` instances while leaving the original instance unchanged.


Spans, Ranges, Starts, and Ends
-------------------------------

You can get the span across a time frame:

.. code-block:: python

    dt = Zulu(2015, 4, 4, 12, 30, 37, 651839)

    dt.span('century')
    # (<Zulu [2000-01-01T00:00:00+00:00]>, <Zulu [2099-12-31T23:59:59.999999+00:00]>)

    dt.span('decade')
    # (<Zulu [2010-01-01T00:00:00+00:00]>, <Zulu [2019-12-31T23:59:59.999999+00:00]>)

    dt.span('year')
    # (<Zulu [2015-01-01T00:00:00+00:00]>, <Zulu [2015-12-31T23:59:59.999999+00:00]>)

    dt.span('month')
    # (<Zulu [2015-04-01T00:00:00+00:00]>, <Zulu [2015-04-30T23:59:59.999999+00:00]>)

    dt.span('day')
    # (<Zulu [2015-04-04T00:00:00+00:00]>, <Zulu [2015-04-04T23:59:59.999999+00:00]>)

    dt.span('hour')
    # (<Zulu [2015-04-04T12:00:00+00:00]>, <Zulu [2015-04-04T12:59:59.999999+00:00]>)

    dt.span('minute')
    # (<Zulu [2015-04-04T12:30:00+00:00]>, <Zulu [2015-04-04T12:30:59.999999+00:00]>)

    dt.span('second')
    # (<Zulu [2015-04-04T12:30:37+00:00]>, <Zulu [2015-04-04T12:30:37.999999+00:00]>)

    dt.span('century', count=3)
    # (<Zulu [2000-01-01T00:00:00+00:00]>, <Zulu [2299-12-31T23:59:59.999999+00:00]>)

    dt.span('decade', count=3)
    # (<Zulu [2010-01-01T00:00:00+00:00]>, <Zulu [2039-12-31T23:59:59.999999+00:00]>)


Or you can get just the start or end of a time frame:

.. code-block:: python

    dt.start_of('day')  # OR dt.start_of_day()
    # <Zulu [2015-04-04T00:00:00+00:00]>

    dt.end_of('day')  # OR dt.end_of_day()
    # <Zulu [2015-04-04T23:59:59.999999+00:00]>

    dt.end_of('year', count=3)  # OR dt.end_of_year()
    # <Zulu [2017-12-31T23:59:59.999999+00:00]>


.. note:: Supported time frames are ``century``, ``decade``, ``year``, ``month``, ``day``, ``hour``, ``minute``, ``second`` and are accessible both from ``start_of(frame)``/``end_of(frame)`` and ``start_of_<frame>()``/``end_of_<frame>``.


You can get a range of time spans:

.. code-block:: python

    start = Zulu(2015, 4, 4, 12, 30)
    end = Zulu(2015, 4, 4, 16, 30)

    for span in Datetime.span_range('hour', start, end):
        print(span)
    # (<Zulu [2015-04-04T12:00:00+00:00]>, <Zulu [2015-04-04T12:59:59.999999+00:00]>)
    # (<Zulu [2015-04-04T13:00:00+00:00]>, <Zulu [2015-04-04T13:59:59.999999+00:00]>)
    # (<Zulu [2015-04-04T14:00:00+00:00]>, <Zulu [2015-04-04T14:59:59.999999+00:00]>)
    # (<Zulu [2015-04-04T15:00:00+00:00]>, <Zulu [2015-04-04T15:59:59.999999+00:00]>)


Or you can iterate over a range of datetimes:

.. code-block:: python

    start = Zulu(2015, 4, 4, 12, 30)
    end = Zulu(2015, 4, 4, 16, 30)

    for dt in Datetime.range('hour', start, end):
        print(dt)
    # <Zulu [2015-04-04T12:30:00+00:00]>
    # <Zulu [2015-04-04T13:30:00+00:00]>
    # <Zulu [2015-04-04T14:30:00+00:00]>


.. note:: Supported range/span time frames are ``century``, ``decade``, ``year``, ``month``, ``day``, ``hour``, ``minute``, ``second``.



Time Deltas
-----------

In addition to having a drop-in replacement for ``datetime``, zulu also has a drop-in replacement for ``timedelta``:

.. code-block:: python

    delta = zulu.delta('1w 3d 2h 32m')
    # <Delta [10 days, 2:32:00]>

    assert isinstance(delta, zulu.Delta)

    from datetime import timedelta
    assert isinstance(delta, timedelta)

    zulu.delta('2:04:13:02.266')
    # <Delta [2 days, 4:13:02.266000]>

    zulu.delta('2 days, 5 hours, 34 minutes, 56 seconds')
    # <Delta [2 days, 5:34:56]>


Other formats that ``zulu.delta`` can parse are:

- ``32m``
- ``2h32m``
- ``3d2h32m``
- ``1w3d2h32m``
- ``1w 3d 2h 32m``
- ``1 w 3 d 2 h 32 m``
- ``4:13``
- ``4:13:02``
- ``4:13:02.266``
- ``2:04:13:02.266``
- ``2 days,  4:13:02`` (``uptime`` format)
- ``2 days,  4:13:02.266``
- ``5hr34m56s``
- ``5 hours, 34 minutes, 56 seconds``
- ``5 hrs, 34 mins, 56 secs``
- ``2 days, 5 hours, 34 minutes, 56 seconds``
- ``1.2 m``
- ``1.2 min``
- ``1.2 mins``
- ``1.2 minute``
- ``1.2 minutes``
- ``172 hours``
- ``172 hr``
- ``172 h``
- ``172 hrs``
- ``172 hour``
- ``1.24 days``
- ``5 d``
- ``5 day``
- ``5 days``
- ``5.6 wk``
- ``5.6 week``
- ``5.6 weeks``


Similar to ``Zulu.time_to/from``, ``Delta`` objects can be humanized with the ``Delta.format`` method:

.. code-block:: python

    delta = zulu.delta('2h 32m')
    # <Delta [2:32:00]>

    delta.format()
    # '3 hours'

    delta.format(add_direction=True)
    # 'in 3 hours'

    zulu.delta('-2h 32m').format(add_direction=True)
    # '3 hours ago'

    delta.format(locale='de')
    # '3 Stunden'

    delta.format(locale='fr', add_direction=True)
    # 'dans 3 heures'

    delta.format(granularity='day')
    # '1 day'

    delta.format(threshold=0)
    # '0 years'

    delta.format(threshold=0.1)
    # '0 days'

    delta.format(threshold=0.2)
    # '3 hours'

    delta.format(threshold=5)
    # '152 minutes'

    delta.format(threshold=155)
    # '9120 seconds'

    delta.format(threshold=155, granularity='minute')
    # '152 minutes'

    delta.format(style='long')
    # '3 hours'

    delta.format(style='short')
    # '3 hr'

    delta.format(style='narrow')
    # '3h'
