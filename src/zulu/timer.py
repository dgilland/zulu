
import time


class Timer(object):
    """Timer that can be used to keep track of elapsed time or to check when a
    timeout has expired.

    Once the timer has been initialized, start the timer with :meth:`start`.
    Repeated calls to :meth:`start` will restart the timer at the
    current time..

    Stop the timer with :meth:`stop`. The timer can then be restarted with
    :meth:`start` with the previously elapsed time carrying over to the next
    timing session (similar to how a stopwatch works).

    Get how much time has elapsed with :meth:`elapsed`. Get whether the timer
    is stopped or started with :meth:`stopped` and :meth:`started`
    respectively.

    When using a timeout (i.e. countdown mode), get the remaining time with
    :meth:`remaining`. Call :meth:`done` to check whether the timeout has
    expired or not.

    Args:
        timeout (int|float, optional): How long, in seconds, the countdown
            timer should last.
    """
    __slots__ = ('timeout', 'started_at', 'stopped_at')

    def __init__(self, timeout=0, autostart=False):
        self.timeout = timeout
        self.reset()

    def __enter__(self):
        """Enter context manager and start the timer."""
        self.start()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        """Exit context manager and stop the timer."""
        self.stop()

    def reset(self):
        """Reset the timer to its initial state."""
        self.started_at = None
        self.stopped_at = None
        return self

    def start(self):
        """Start the timer."""
        if (self.stopped_at is not None and
                self.started_at is not None and
                self.started_at < self.stopped_at):
            offset = self.stopped_at - self.started_at
        else:
            offset = 0

        self.started_at = time.time() - offset
        self.stopped_at = None
        return self

    def stop(self):
        """Stop the timer."""
        self.stopped_at = time.time()
        return self

    def started(self):
        """Return whether the timer has been started."""
        return (self.started_at is not None and
                (self.stopped_at is None or
                 self.stopped_at < self.started_at))

    def stopped(self):
        """Return whether the timer is stopped."""
        return (self.started_at is None or
                (self.stopped_at is not None and
                 self.stopped_at >= self.started_at))

    def elapsed(self):
        """Return how long the timer has been running."""
        if self.started_at is None:
            return 0
        elif self.stopped_at is not None:
            return self.stopped_at - self.started_at
        else:
            return time.time() - self.started_at

    def remaining(self):
        """Return how much time is remaining before timer runs out."""
        return self.timeout - self.elapsed()

    def done(self):
        """Return whether :attr:`timeout` has expired and the countdown is
        done.
        """
        return self.elapsed() >= self.timeout
