"""Log line for symbol_please."""
import re

import dateutil.parser

LOG_REGEX = re.compile(r'^\[(?P<time>[^\]]+)\] (?P<message>.+)$')


class LogLine():
    """An object that represents a single log line."""

    def __init__(self, line, line_id):
        """Initialize the log line from its string representation."""
        match = LOG_REGEX.match(line)
        if match is None:
            raise ValueError(
                "Given line does not match expected log format: '{}'"
                .format(line))

        self.line_id = line_id
        self.raw_line = line
        self.raw_timestamp = match.group('time')
        self.timestamp = dateutil.parser.parse(self.raw_timestamp)
        self.message = match.group('message')

    def __repr__(self):
        return self.message
