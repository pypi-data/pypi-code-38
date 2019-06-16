import sys
import cutie
from collections import namedtuple
from functools import wraps
from pathlib import Path
from agw import Automater
from .util import Counter


def data_generator(fields, header_row=True, separator=","):

    DataObject = namedtuple("DataObject", fields)

    def iter_lines(filepath):
        with filepath.open(mode="r") as fh_:
            for index, line in enumerate(fh_.readlines()):
                if index == 0 and header_row is True:
                    continue
                if not line or line.startswith("#"):
                    continue
                data = DataObject(*[i.strip() for i in line.strip().split(separator)])
                yield index, data

    return iter_lines


class MacroDataFileHandler(object):
    def __init__(
        self,
        data_fields,
        header_row=False,
        separator=",",
        line_pause=False,
        line_start=False,
    ):
        self.data_fields = data_fields
        self._iterate = data_generator(data_fields, header_row, separator)
        self.line_pause = 0
        self.line_start = 0

    def get_inputs(self):
        line_pause = cutie.get_number("  Pause after every N lines: ")
        self.line_pause = int(line_pause) if line_pause else None

        skip_to_line = cutie.get_number("  Start from line: ")
        self.skip_to_line = int(skip_to_line) if skip_to_line else None

    def iter(self, filepath):
        filepath = Path(filepath)
        ai = Automater()

        line_count = Counter()
        pause_count = Counter()

        for index, data in self._iterate(filepath):

            if self.skip_to_line and line_count.next() < self.skip_to_line:
                continue

            if self.line_pause and pause_count.next() == self.line_pause:
                pause_count.reset()
                if ai.msgbox.confirm("continue?") == "No":
                    print("Operation concelled.")
                    sys.exit(0)

            yield index, data


def iterfile(data_fields, file_arg="--data-file", header_row=False, separator=","):
    """Convenience decorator that wrapps creation of file iterator.
    """

    def _iterfile(func):

        handler = MacroDataFileHandler(
            data_fields, header_row=header_row, separator=separator
        )

        @wraps(func)
        def __iterfile(ai, filepath):
            iterator = handler.iter(filepath)
            ai.get_data_handling_inputs = handler.get_inputs
            return func(ai, iterator)

        __iterfile.file_arg = file_arg

        return __iterfile

    return _iterfile
