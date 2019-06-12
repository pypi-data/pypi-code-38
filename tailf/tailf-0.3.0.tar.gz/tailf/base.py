import os


class TailBase:
    def __init__(self, path):
        self._path = path
        head, tail = os.path.split(path)
        if not tail:
            raise ValueError("directory path")
        if not head:
            head = "."
        self._dir, self._filename = head, tail
        self._file = None
        self._buffers = []  # it's reversed
        self._truncated = False
        self._truncation_handled = True
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        """Finalize this Tail object and free underlying resources.

        It is allowed to close an already closed Tail object.
        """
        if self.closed:
            return
        self._assure_closed()
        self.closed = True

    def is_truncated(self):
        """Returns True if truncation has been previously hit while reading the
        file.

        Truncation is not consumed, so the following calls to
        `is_truncated()` keep returning True.
        """
        return self._truncated and not self._truncation_handled

    def get_truncated(self):
        """Returns True if truncation has been previously hit while reading the
        file.

        Truncation is consumed, so the following calls to `get_truncated()`
        return False until another truncation is hit.
        """
        value = self.is_truncated()
        self._truncated = False
        self._truncation_handled = True
        return value

    def _check_truncated_pre_data(self):
        """do truncation checks before reading data"""
        if self._file is not None:
            stat = os.fstat(self._file.fileno())
            if stat.st_size < self._file_pos:
                return True
            self._file_id = (stat.st_dev, stat.st_ino)

    def _check_truncated_post_data(self):
        """do truncation checks after reading data"""
        try:
            stat = os.stat(self._path)
        except FileNotFoundError:
            return True
        if self._file_id != (stat.st_dev, stat.st_ino):
            return True

    def _assure_open(self):
        if self._file is None or self._file.closed:
            self._file = None
            try:
                self._file = open(self._path, "rb")
            except FileNotFoundError:
                return False
            self._file_pos = 0  # only valid if self.file is not None
        return True

    def _assure_closed(self):
        if self._file is not None:
            if not self._file.closed:
                self._file.close()
            self._file = None

    def _read1(self, size=-1):
        """Read and return up to `size` bytes, with at most one call to
        underlying file `read()` (or `readinto()`) method.

        If size=-1 (the default), and arbitrary number of bytes are returned
        (more than zero unless EOF or truncation was encountered).
        """
        # 1. Check if previously buffered data exist
        if len(self._buffers):
            assert not self.is_truncated(), "invariant"
            buf = self._buffers[-1]
            if size == -1 or len(buf) <= size:
                del self._buffers[-1]
            else:
                buf = buf[:size]
                self._buffers[-1] = self._buffers[-1][size:]
            return buf

        # 2. Check if there is still an unhandled truncation
        if self.is_truncated():
            return b""

        # 3. Check if file is available
        if not self._assure_open():
            return b""

        # 4. Check if there was a new truncation
        if self._check_truncated_pre_data():
            self._assure_closed()
            self._truncated = True
            return b""

        # 5. Go for file data
        data = self._file.read(size)
        if len(data) > 0:
            self._truncation_handled = False
            self._file_pos += len(data)
            return data

        # 6. Check if there is new truncation
        if self._check_truncated_post_data():
            self._assure_closed()
            self._truncated = True

        return b""

    def _decode(self, data, start=0, end=None):
        """Copy data from `self._buffer` into `bytes` or `string`
        """
        if end is None:
            end = len(data)
        b = bytes(data[start:end])
        if len(b):
            self._truncation_handled = (
                False
            )  # if data size > 0, unmark previously consumed truncation
        # TODO apply encoding
        return b

    def _push_buffer(self, data):
        assert isinstance(data, bytes)
        if len(data):
            self._buffers.append(data)
