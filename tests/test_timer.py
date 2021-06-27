from contextlib import contextmanager
from unittest import mock

import pytest

from zulu import Timer


parametrize = pytest.mark.parametrize


@contextmanager
def mock_time(epoch):
    with mock.patch("time.time", return_value=epoch):
        yield


def test_timer_timing():
    timer = Timer()

    assert timer.stopped()
    assert timer.elapsed() == 0

    with mock_time(1):
        timer.start()

    assert timer.started()
    assert not timer.stopped()

    with mock_time(5):
        timer.stop()

    assert not timer.started()
    assert timer.stopped()

    assert timer.elapsed() == 4


def test_timer_toggle():
    timer = Timer()

    with mock_time(5):
        timer.start()

    with mock_time(10):
        timer.stop()
        assert timer.elapsed() == 5

    with mock_time(15):
        timer.start()

    with mock_time(30):
        timer.stop()
        assert timer.elapsed() == 20


def test_timer_timeout():
    timer = Timer(timeout=10)

    with mock_time(0):
        timer.start()
        assert timer.elapsed() == 0
        assert timer.remaining() == 10
        assert not timer.done()

    with mock_time(4):
        assert timer.elapsed() == 4
        assert timer.remaining() == 6
        assert not timer.done()

    with mock_time(10):
        assert timer.elapsed() == 10
        assert timer.remaining() == 0
        assert timer.done()


def test_timer_reset():
    timer = Timer()

    timer.start()
    timer.stop()

    assert timer.started_at > 0
    assert timer.stopped_at > 0

    timer.reset()

    assert timer.started_at is None
    assert timer.stopped_at is None


def test_timer_contextmanager():
    timer = Timer()

    with timer:
        assert timer.started()

    assert timer.stopped()
