""" A watchdog keeping an eye on the time """

from time import time, strftime
from pathlib import Path
from hilde.helpers.warnings import warn


class WallTimeWatchdog:
    """ Watched the walltime """

    def __init__(
        self,
        walltime=None,
        history=10,
        buffer=2,
        log="watchdog.log",
        verbose=True,
        **kwargs,
    ):
        """ Watchdog that controls the walltime everytime it is called

        Args:
            walltime (int): Walltime in seconds
            history (int, optional):
                Defaults to 5. How many steps should be used to project the runtime
            buffer (int, optional):
                Defaults to 2. How many steps of buffer before watchdog should alert.
        """

        if walltime is None:
            warn("walltime not set, use 1 day")
            walltime = 86400

        self.buffer = buffer
        self.start_time = time()
        self.walltime = walltime + time()
        self.history = [time()]
        self.n_calls = 0
        self.logfile = None
        self.max_depth = history
        self.verbose = verbose

        if log is not None:
            self.logfile = Path(log)

    def __call__(self):
        """ Call the watchdog

        Returns:
            bool: Are we approaching the walltime or is a 'stop' flag present?
        """

        # update history
        self.history.append(time())

        stop_file = Path("stop")
        if stop_file.exists():
            import sys

            stop_file.unlink()

            with self.logfile.open("a") as f:
                f.write("*** stop file found")
            sys.exit("*** Watchdog: stop flag was found: remove it and exit.")

        # is sufficient time left?
        time_is_up = time() + self.buffer_time > self.walltime

        # delete last step from history
        if len(self.history) > self.max_depth:
            self.history = self.history[1:]

        # log the step
        self.log()
        self.n_calls += 1

        if time_is_up and self.verbose:
            warn("Watchdog: running out of time!")

        # return information if time is up
        return time_is_up

    @property
    def increment_per_step(self):
        """ compute increment per step based on history """
        hist = self.history

        if len(hist) < 2:
            return 0

        return (hist[-1] - hist[0]) / (len(hist) - 1)

    @property
    def time_left(self):
        """ how much time is left? """
        return self.walltime - time()

    @property
    def buffer_time(self):
        """ approximate additional time the number of buffer steps would need """
        return self.increment_per_step * self.buffer

    @property
    def elapsed(self):
        """ Return elapsed time since start """
        return time() - self.start_time

    def log(self, mode="a"):
        """ Log some timings """

        if self.logfile is None:
            return

        info_str = ""
        if self.n_calls == 0:
            mode = "w"
            info_str = f"# Walltime Watchdog \n"
            info_str += f"#   walltime:     {self.time_left:.0f}s\n"
            info_str += f"#   buffer steps: {self.buffer}\n"
            info_str += f"# {'Time':17s} " + " ".join(
                f"{s:>10s}"
                for s in ("n_call", "increment", "buffer_time", "time_left", "elapsed")
            )
            info_str += "\n"

        timestr = strftime("%Y/%m/%d %H:%M:%S")

        info_str += f"{timestr} {self.n_calls:10d} " + " ".join(
            f"{s:10.1f}"
            for s in (
                self.increment_per_step,
                self.buffer_time,
                self.time_left,
                self.elapsed,
            )
        )
        info_str += "\n"

        with self.logfile.open(mode) as f:
            f.write(info_str)
