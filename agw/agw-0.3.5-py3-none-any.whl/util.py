from pathlib import Path
from datetime import datetime
from itertools import chain


class Counter:
    def __init__(self, start=0):
        self.count = start
        self.start = start

    def reset(self):
        self.count = self.start

    def next(self):
        self.count += 1
        return self.count


class Timer:
    def __init__(self):
        self._start_time = None
        self._end_time = None
        self._duration = None

    def reset(self):
        self._start_time = None
        self._end_time = None
        self._duration = None

    def start(self):
        self._start_time = datetime.now()

    def stop(self):
        self._end_time = datetime.now()
        self._duration = self._end_time - self._start_time

    def __str__(self):
        return str(self._duration)


def fetch_file_argument(file_arg, argv=None):
    """
    Arguments for `file_arg` can either be: "0" which indicates to use the first cli arg,
    otherwise, the `file_arg` is expected to be a keyword argument like `--data-file`.

    """
    if argv:
        args = argv
    else:
        import sys
        args = sys.argv[1:]

    err_msg = f"You must provide a data file argument! ({file_arg})."

    if len(args) == 0:
        raise Exception(err_msg.format(file_arg=file_arg))

    first_arg = True if file_arg == "0" else False

    args_normalized = list(chain(*[a.split("=") for a in args]))

    if first_arg:
        file_arg = args[0]

    elif file_arg in args_normalized:
        file_arg = args_normalized[args_normalized.index(file_arg) + 1]

    else:
        raise Exception(err_msg.format(file_arg=file_arg))

    pth = Path(file_arg)

    if pth.exists():
        return pth

    raise Exception(f"Provided path does not exist! {pth}")
