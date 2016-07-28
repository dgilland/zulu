****
zulu
****

|version| |travis| |coveralls| |license|


A drop-in replacement for native datetimes that embraces UTC


Links
=====

- Project: https://github.com/dgilland/zulu
- Documentation: https://zulu.readthedocs.io
- PyPI: https://pypi.python.org/pypi/zulu/
- TravisCI: https://travis-ci.org/dgilland/zulu


Features
========

- Supported on Python 2.7 and Python >= 3.4
- All datetime objects converted and stored as UTC.
- Parses ISO8601 formatted strings and POSIX timestamps by default.
- Timezone representation applied only during string output formatting or when casting to native datetime object.
- Drop-in replacement interface for native datetime objects.


Quickstart
==========

Install using pip:


::

    pip install zulu


Zulu's main type is ``zulu.DateTime`` which represents a fixed UTC datetime object.

.. code-block:: python

    import zulu

    dt = zulu.now()
    # <DateTime [2016-07-25T19:33:18.137493+00:00]>

    assert isinstance(dt, zulu.DateTime)


It's a drop-in replacement for native datetime objects (it inherits from ``datetime.datetime``) but deals only with UTC time zones internally.

.. code-block:: python

    assert dt.year == 2016
    assert dt.month == 7
    assert dt.day == 25
    assert dt.hour == 19
    assert dt.minute == 33
    assert dt.second == 18
    assert dt.microsecond == 137493
    assert dt.tzname() == 'UTC'

    dt.isoformat()
    # '2016-07-25T19:33:18.137493+00:00'

    dt.timestamp()
    # 1469475198.137493

    dt.date()
    # datetime.date(2016, 7, 25)

    dt.time()
    # datetime.time(19, 33, 18, 137493)


Easy access to a naive datetime object:

.. code-block:: python


    dt.naive
    # datetime.datetime(2016, 7, 25, 19, 33, 18, 137493)


It can easily apply timedelta's using the ``shift`` method:

.. code-block:: python

    shifted = dt.shift(hours=-5, minutes=10)
    # <DateTime [2016-07-25T14:43:18.137493+00:00]>

    assert shifted is not dt


Or replace datetime attributes:

.. code-block:: python

    replaced = dt.replace(hour=14, minute=43)
    # <DateTime [2016-07-25T14:43:18.137493+00:00]>

    assert replaced is not dt


.. note:: Since ``DateTime`` is meant to be immutable, both ``shift`` and ``replace`` return new ``DateTime`` instances while leaving the original instance unchanged.

You can get the time span of any unit:

.. code-block:: python

    dt = DateTime(2015, 4, 4, 12, 30)
    dt.span('century')
    # (<DateTime [2000-01-01T00:00:00+00:00]>, <DateTime [2099-12-31T23:59:59.999999+00:00]>)

    dt.span('decade')
    # (<DateTime [2010-01-01T00:00:00+00:00]>, <DateTime [2019-12-31T23:59:59.999999+00:00]>)

    dt.span('year')
    # (<DateTime [2015-01-01T00:00:00+00:00]>, <DateTime [2015-12-31T23:59:59.999999+00:00]>)

    dt.span('century', count=3)
    # (<DateTime [2000-01-01T00:00:00+00:00]>, <DateTime [2299-12-31T23:59:59.999999+00:00]>)

    dt.span('decade', count=3)
    # (<DateTime [2010-01-01T00:00:00+00:00]>, <DateTime [2039-12-31T23:59:59.999999+00:00]>)


Or you can also get the start and end of any unit:

.. code-block:: python

    dt = DateTime(2015, 4, 4, 12, 30)
    dt.start_of('century')
    # <DateTime [2000-01-01T00:00:00+00:00]>

    dt.start_of('decade')
    # <DateTime [2010-01-01T00:00:00+00:00]>

    dt.start_of('year')
    # <DateTime [2015-01-01T00:00:00+00:00]>

    dt.end_of('century')
    # <DateTime [2099-12-31T23:59:59.999999+00:00]>

    dt.end_of('decade')
    # <DateTime [2019-12-31T23:59:59.999999+00:00]>

    dt.end_of('year', count=3)
    # <DateTime [2017-12-31T23:59:59.999999+00:00]>


.. note:: Supported units are ``century``, ``decade``, ``year``, ``month``, ``day``, ``hour``, ``minute``, ``second``.

Time zones other than UTC are not expressable within a ``DateTime`` instance. Other time zones are only ever applied when either casting a ``DateTime`` object as a native datetime (via ``DateTime.astimezone``) or during string formatting (via ``DateTime.format``). ``DateTime`` understands both ``tzinfo`` objects and ``pytz.timezone`` strings.


.. code-block:: python

    local = dt.astimezone()
    # same as doing dt.astimezone('local')
    # datetime.datetime(2016, 7, 25, 15, 33, 18, 137493, tzinfo=<DstTzInfo 'America/New_York' EDT-1 day, 20:00:00 DST>)

    pacific = dt.astimezone('US/Pacific')
    # datetime.datetime(2016, 7, 25, 12, 33, 18, 137493, tzinfo=<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>)

    import pytz
    mountain = dt.astimezone(pytz.timezone('US/Mountain'))
    # datetime.datetime(2016, 7, 25, 13, 33, 18, 137493, tzinfo=<DstTzInfo 'US/Mountain' MDT-1 day, 18:00:00 DST>)


Currently, ``DateTime`` only supports `strftime/strptime-style <https://docs.python.org/3.5/library/datetime.html#strftime-and-strptime-behavior>`_ tokens during parsing and formatting, but there are plans to support `Arrow's format tokens <https://arrow.readthedocs.io/en/latest/#tokens>`_.

.. code-block:: python

    dt.format('%Y-%m-%d %H:%M:%S%z')
    # '2016-07-25 19:33:18+0000'

    dt.format('%Y-%m-%d %H:%M:%S%z', tz='US/Eastern')
    # '2016-07-25 15:33:18-0400'

    zulu.parse('2016-07-25 15:33:18-0400', '%Y-%m-%d %H:%M:%S%z')
    # <DateTime [2016-07-25T19:33:18+00:00]>


By default, ``zulu.parse`` will look for either an ISO 8601 formatted string or a POSIX timestamp while assuming that in the absence of an explicit timezone, UTC will be used:

.. code-block:: python

    zulu.parse('2016-07-25 15:33:18-0400')
    # <DateTime [2016-07-25T19:33:18+00:00]>

    zulu.parse('2016-07-25')
    # <DateTime [2016-07-25T00:00:00+00:00]>

    zulu.parse('2016-07-25 19:33')
    # <DateTime [2016-07-25T19:33:00+00:00]>

    zulu.parse(1469475198.0, 'timestamp')
    # <DateTime [2016-07-25T19:33:18+00:00]>


Local time zones can be substituted for naive datetimes by setting ``default_tz``:

.. code-block:: python

    zulu.parse('2016-07-25', default_tz='US/Eastern')
    # <DateTime [2016-07-25T04:00:00+00:00]>

    # default ignored when string provides it
    zulu.parse('2016-07-25T15:33:18-0700', default_tz='US/Eastern')
    # <DateTime [2016-07-25T22:33:18+00:00]>


Why Zulu?
=========

Why zulu instead of `native datetimes <https://docs.python.org/3.5/library/datetime.html#datetime-objects>`_:

- Zulu has extended datetime features such as ``parse()``, ``format()``, ``shift()``, and `pytz <http://pytz.sourceforge.net/>`_ timezone support.
- Parses ISO 8601 and timestamps by default without any extra arguments.
- Easier to reason about ``DateTime`` objects since they are only ever UTC datetimes.
- Clear delineation between UTC and other time zones where timezone representation is only applicable for display or conversion to native datetime.


Why zulu instead of `Arrow <https://arrow.readthedocs.io>`_:

- Zulu is a drop-in replacement for native datetimes (inherits from ``datetime.datetime``). No need to convert using ``arrow.datetime`` when you need a datetime (zulu is always a datetime).
- Stricter parsing to avoid silent errors. For example, one might expect ``arrow.get('02/08/1987', 'MM/DD/YY')`` to fail (input does not match format) but it gladly returns ``<Arrow [2019-02-08T00:00:00+00:00]>`` whereas ``zulu.parse('02/08/1987', '%m/%d/%y')`` throws ``zulu.parser.ParseError: Value "02/08/1987" does not match any format in ['%m/%d/%y']``.
- Avoids timezone/DST shifting bugs by only dealing with UTC datetimes when applying timedeltas or performing other calculations.


For more details, please see the full documentation at https://zulu.readthedocs.io.



.. |version| image:: https://img.shields.io/pypi/v/zulu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/zulu/

.. |travis| image:: https://img.shields.io/travis/dgilland/zulu/master.svg?style=flat-square
    :target: https://travis-ci.org/dgilland/zulu

.. |coveralls| image:: https://img.shields.io/coveralls/dgilland/zulu/master.svg?style=flat-square
    :target: https://coveralls.io/r/dgilland/zulu

.. |license| image:: https://img.shields.io/pypi/l/zulu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/zulu/
