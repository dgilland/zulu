Changelog
=========


- Add ``DateTime.datetime`` property that returns a native datetime.
- Add ``DateTime.add`` and ``DateTime.sub`` methods.
- Make ``DateTime.shift/add/sub`` use ``dateutil.relativedelta.relativedelta`` under the hood which brings new shiftable arguments: years and months
- Drop support for milliseconds from ``DateTime.shift/add/sub``. **breaking change**


v0.1.2 (2016-07-26)
-------------------

- Don't pin install requirements to a specific version; use ``>=`` instead.


v0.1.1 (2016-07-26)
-------------------

- Fix bug in ``DateTime.naive`` that resulted in a DateTime object being returned instead of a native datetime.


v0.1.0 (2016-07-26)
-------------------

- First release.
