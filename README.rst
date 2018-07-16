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

- Supported on Python 2.7 and Python 3.4+
- All datetime objects converted and stored as UTC.
- Parses ISO8601 formatted strings and POSIX timestamps by default.
- Timezone representation applied only during string output formatting or when casting to native datetime object.
- Drop-in replacement for native datetime objects.


Quickstart
==========

Install using pip:


::

    pip install zulu


.. code-block:: python

    import zulu

    zulu.now()
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    dt = zulu.parse('2016-07-25T19:33:18.137493+00:00')
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    dt = zulu.create(2016, 7, 25, 19, 33, 18, 137493)
    # <Zulu [2016-07-25T19:33:18.137493+00:00]>

    dt.isoformat()
    # '2016-07-25T19:33:18.137493+00:00'

    dt.timestamp()
    # 1469475198.137493

    dt.naive
    # datetime.datetime(2016, 7, 25, 19, 33, 18, 137493)

    dt.datetime
    # datetime.datetime(2016, 7, 25, 19, 33, 18, 137493, tzinfo=<UTC>)

    dt.format('%Y-%m-%d')
    # 2016-07-25

    dt.format('YYYY-MM-dd')
    # 2016-07-25

    dt.format("E, MMM d, ''YY")
    # "Mon, Jul 25, '16"

    dt.format("E, MMM d, ''YY", locale='de')
    # "Mo., Juli 25, '16"

    dt.format("E, MMM d, ''YY", locale='fr')
    # "lun., juil. 25, '16"

    dt.shift(hours=-5, minutes=10)
    # <Zulu [2016-07-25T14:43:18.137493+00:00]>

    dt.replace(hour=14, minute=43)
    # <Zulu [2016-07-25T14:43:18.137493+00:00]>

    dt.start_of('day')
    # <Zulu [2016-07-25T00:00:00+00:00]>

    dt.end_of('day')
    # <Zulu [2016-07-25T23:59:59.999999+00:00]>

    dt.span('hour')
    # (<Zulu [2016-07-25T19:00:00+00:00]>, <Zulu [2016-07-25T19:59:59.999999+00:00]>)

    dt.time_from(dt.end_of('day'))
    # '4 hours ago'

    dt.time_to(dt.end_of('day'))
    # 'in 4 hours'

    list(zulu.range('hour', dt, dt.shift(hours=4)))
    # [Zulu [2016-07-25T19:33:18.137493+00:00]>,
    #  Zulu [2016-07-25T20:33:18.137493+00:00]>,
    #  Zulu [2016-07-25T21:33:18.137493+00:00]>,
    #  Zulu [2016-07-25T22:33:18.137493+00:00]>]

    list(zulu.span_range('minute', dt, dt.shift(minutes=4)))
    # [(Zulu [2016-07-25T19:33:00+00:00]>, Zulu [2016-07-25T19:33:59.999999+00:00]>),
    #  (Zulu [2016-07-25T19:34:00+00:00]>, Zulu [2016-07-25T19:34:59.999999+00:00]>),
    #  (Zulu [2016-07-25T19:35:00+00:00]>, Zulu [2016-07-25T19:35:59.999999+00:00]>),
    #  (Zulu [2016-07-25T19:36:00+00:00]>, Zulu [2016-07-25T19:36:59.999999+00:00]>)]

    zulu.parse_delta('1w 3d 2h 32m')
    # <Delta [10 days, 2:32:00]>

    zulu.parse_delta('2:04:13:02.266')
    # <Delta [2 days, 4:13:02.266000]>

    zulu.parse_delta('2 days, 5 hours, 34 minutes, 56 seconds')
    # <Delta [2 days, 5:34:56]>


Why Zulu?
=========

Why zulu instead of `native datetimes <https://docs.python.org/3.5/library/datetime.html#datetime-objects>`_:

- Zulu has extended datetime features such as ``parse()``, ``format()``, ``shift()``, and `python-dateutil`_ timezone support.
- Parses ISO8601 and timestamps by default without any extra arguments.
- Easier to reason about ``Zulu`` objects since they are only ever UTC datetimes.
- Clear delineation between UTC and other time zones where timezone representation is only applicable for display or conversion to native datetime.
- Supports more string parsing/formatting options using `Unicode date patterns`_ as well as ``strptime/strftime`` directives.


Why zulu instead of `Arrow`_:

- Zulu is a drop-in replacement for native datetimes (inherits from ``datetime.datetime``). No need to convert using ``arrow.datetime`` when you need a datetime (zulu is always a datetime).
- Stricter parsing to avoid silent errors. For example, one might expect ``arrow.get('02/08/1987', 'MM/DD/YY')`` to fail (input does not match format) but it gladly returns ``<Arrow [2019-02-08T00:00:00+00:00)`` whereas ``zulu.parse('02/08/1987', '%m/%d/%y')`` throws ``zulu.parser.ParseError: Value "02/08/1987" does not match any format in ['%m/%d/%y']``.
- Avoids timezone/DST shifting bugs by only dealing with UTC datetimes when applying timedeltas or performing other calculations.
- Supports ``strptime/strftime`` as well as `Unicode date patterns`_ for string parsing/formatting.


Special Thanks
==============

Special thanks goes out to the authors/contributors of the following libraries that have made it possible for ``zulu`` to exist:

- `Babel`_
- `iso8601`_
- `python-dateutil`_
- `pytimeparse`_
- `pytz`_


For the full documentation, please visit https://zulu.readthedocs.io.



.. _Unicode date patterns: http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table
.. _Arrow: https://arrow.readthedocs.io
.. _Babel: https://github.com/python-babel/babel
.. _iso8601: https://bitbucket.org/micktwomey/pyiso8601
.. _python-dateutil: https://github.com/dateutil/dateutil
.. _pytimeparse: https://github.com/wroberts/pytimeparse
.. _pytz: http://pythonhosted.org/pytz

.. |version| image:: https://img.shields.io/pypi/v/zulu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/zulu/

.. |travis| image:: https://img.shields.io/travis/dgilland/zulu/master.svg?style=flat-square
    :target: https://travis-ci.org/dgilland/zulu

.. |coveralls| image:: https://img.shields.io/coveralls/dgilland/zulu/master.svg?style=flat-square
    :target: https://coveralls.io/r/dgilland/zulu

.. |license| image:: https://img.shields.io/pypi/l/zulu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/zulu/
