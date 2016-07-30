Changelog
=========


(unreleased)
------------

- Add ``DateTime.datetime`` property that returns a native datetime.
- Add ``DateTime.fromgmtime`` that creates a ``DateTime`` from a UTC based ``time.struct_time``.
- Add ``DateTime.fromlocaltime`` that creates a ``DateTime`` from a local ``time.struct_time``.
- Add ``DateTime.add`` and ``DateTime.sub`` methods.
- Make ``DateTime.shift/add/sub`` use ``dateutil.relativedelta.relativedelta`` under the hood which brings new shiftable arguments: years and months
- Drop support for milliseconds from ``DateTime.shift/add/sub``. **breaking change**
- Make ``DateTime.parse/format`` understand a subset of `Unicode date patterns <http://www.unicode.org/reports/tr35/tr35-19.html#Date_Field_Symbol_Table>`_ by translating them to strptime/strftime format directives.
- Set defaults for year (1970), month (1), and day (1) arguments to new ``DateTime`` objects. Creating a new ``DateTime`` now defaults to the start of the POSIX epoch.


v0.1.2 (2016-07-26)
-------------------

- Don't pin install requirements to a specific version; use ``>=`` instead.


v0.1.1 (2016-07-26)
-------------------

- Fix bug in ``DateTime.naive`` that resulted in a DateTime object being returned instead of a native datetime.


v0.1.0 (2016-07-26)
-------------------

- First release.
