# SPDX-License-Identifier: GPL-3.0-or-later


class Splitter:
    def __init__(self, *, sep, chunk_ready_callback, low, high):
        self._sep = sep
        self._chunk_ready_callback = chunk_ready_callback
        self._empty_buffer = type(
            sep
        )()  # Make an empty string or byte sequence
        self._buf = self._empty_buffer
        self._low = low
        self._high = high
        self._overflow = False

    def write(self, data):
        callback = self._chunk_ready_callback
        self._buf += data

        start = 0
        end = self._find_chunk_end(start)
        while end:
            callback(self._buf[start:end])
            start = end
            end = self._find_chunk_end(start)

        if start:
            self._buf = self._buf[start:]

    def flush(self):
        if self._buf:
            callback = self._chunk_ready_callback
            callback(self._buf)
            self._buf = self._empty_buffer
            self._overflow = False

    def _find_chunk_end(self, start):
        window_size = self._low if self._overflow else self._high
        pos = self._buf.find(self._sep, start, start + window_size)

        if pos != -1:
            self._overflow = False
            return pos + len(self._sep)

        if len(self._buf) - start >= window_size:
            self._overflow = True
            return start + self._low

        return None


def format_bytes_for_logging(data):
    return repr(data)[1:]


class LogfileRead:
    def __init__(self, logger):
        log_function = lambda line: logger.debug(
            "< " + format_bytes_for_logging(line)
        )
        self._splitter = Splitter(
            sep=b"\n", chunk_ready_callback=log_function, low=20, high=120
        )

    def write(self, data):
        self._splitter.write(data)

    def flush(self):
        pass

    def log_remaining_text(self):
        self._splitter.flush()


class LogfileSend:
    def __init__(self, logger):
        self._logger = logger

    def write(self, data):
        sep = b"\n"
        lines = data.split(sep)
        for line in lines[:-1]:
            self._log(line + sep)
        last_line = lines[-1]
        # For consistency make at least one call to logger per write, even if we
        # only have one line and it is empty.
        if len(lines) == 1 or last_line:
            self._log(last_line)

    def flush(self):
        pass

    def _log(self, line):
        self._logger.debug("> " + format_bytes_for_logging(line))
