import io
import os


class InternalBuffer:
    def __init__(self, size):
        assert size > 0
        self.size = size
        self._buffer = bytearray(size)
        self._left = self._right = 0

    def get(self, size=-1):
        right = self._right if size < 0 else min(self._left + size, self._right)
        return bytes(self._buffer[self._left : right])

    def pop(self, size=-1):
        result = self.get(size)
        self.clear(size)
        return result

    def clear(self, size=-1):
        if size == -1:
            self._left = self._right = 0
        else:
            self._left = min(self._left + size, self._right)

    def readfrom(self, f):
        self._left = 0
        self._right = f.readinto(self._buffer)

    def __len__(self):
        return self._right - self._left

    def __bool__(self):
        return bool(len(self))

    def find(self, sub, start=0, end=None):
        left = self._left + start
        if end is None:
            right = self._right
        else:
            right = self._left + end
        index = self._buffer.find(sub, left, right)
        if index >= 0:
            index -= self._left
        return index


class TailBase:
    def __init__(self, path, buffer_size=io.DEFAULT_BUFFER_SIZE):
        self._path = path
        head, tail = os.path.split(path)
        if not tail:
            raise ValueError("directory path")
        if not head:
            head = "."
        self._dir, self._filename = head, tail
        self._file = None
        self._truncated = False
        self._truncation_handled = True
        self.closed = False
        self._buffer = InternalBuffer(buffer_size)

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
                buffering = self._buffer.size
                if buffering == 1:
                    buffering = 0  # no buffering, instead of line buffering
                self._file = open(self._path, "rb", buffering=self._buffer.size)
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

        DEPRECATED in favor of _do_read1
        """
        self._do_read1()
        return self._buffer.pop(size)

    def _do_read1(self):
        """Read some bytes, with at most one call to underlying file `read()`
        (or `readinto()`) method. Place the bytes into internal buffer.

        If size=-1 (the default), arbitrary number of bytes are returned (more
        than zero unless EOF or truncation was encountered).
        """
        # 1. Check if previously buffered data exist
        if self._buffer:
            assert not self.is_truncated(), "invariant"
            return

        # 2. Check if there is still an unhandled truncation
        if self.is_truncated():
            return

        # 3. Check if file is available
        if not self._assure_open():
            return

        # 4. Check if there was a new truncation
        if self._check_truncated_pre_data():
            self._assure_closed()
            self._truncated = True
            return

        # 5. Go for file data
        self._buffer.readfrom(self._file)
        if self._buffer:
            self._truncation_handled = False
            self._file_pos += len(self._buffer)
            return

        # 6. Check if there is new truncation
        if self._check_truncated_post_data():
            self._assure_closed()
            self._truncated = True

    def _decode(self, data, start=0, end=None):
        """Copy data from `data` into `bytes` or `string`
        """
        if end is None:
            end = len(data)
        b = bytes(data[start:end])
        if len(b):
            # if data size > 0, unmark previously consumed truncation
            self._truncation_handled = False
        # TODO apply encoding
        return b
