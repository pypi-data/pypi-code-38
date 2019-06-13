import os
import os.path

from .const import *

__all__ = ["Tail"]


class Tail:
    """Follow file contents change.

    This class is iterable, and yields data portions as `bytes` objects and
    Truncated events until depleted. After raising StopIteration, new events
    may appear later.

    :ivar closed: True if this Tail object has been closed. False initially.

    :Limitations:

    * Truncation detection is unreliable in general. It is primarily tracked by
      file size decrease, which sometimes can be unreliable. In cases when a file
      grows large and is truncated seldom, this is sufficient.
    """

    buffer_size = 4096

    def __init__(self, path):
        self.path = path
        head, tail = os.path.split(path)
        if not tail:
            raise ValueError("directory path")
        if not head:
            head = "."
        self.dir, self.filename = head, tail
        self.file = None
        self._truncated = False
        self._just_truncated = True
        self.closed = False

    def read(self, size=-1):
        """Read data from the file.

        This works similar to `read()` method of a file-like object. If the
        file hits EOF, this keeps returning `b''`. If the file was truncated,
        this also keeps returning `b''` until truncation event is consumed (see
        `Tail.get_truncated()`).
        """
        if self.closed:
            raise ValueError("closed")
        if self._truncated:
            return b""
        if self._check_truncated_pre_data():
            if self.file is not None:
                if not self.file.closed:
                    self.file.close()
                self.file = None
            if not self._just_truncated:
                self._truncated = True
            return b""
        data = self.file.read(size)
        if len(data):
            self._file_pos += len(data)
            self._just_truncated = False
            return data
        if self._check_truncated_post_data():
            if self.file is not None:
                if not self.file.closed:
                    self.file.close()
                self.file = None
            if not self._just_truncated:
                self._truncated = True
            return b""
        return b""

    def get_truncated(self):
        """Consume truncation event.

        If the file was truncated at current location, returns True and
        consumes the truncation event (i.e. subsequent calls to
        `get_truncated()` would return False. Otherwise, returns False.
        """

        result = self._truncated
        self._truncated = False
        self._just_truncated = result
        return result

    def is_truncated(self):
        """Check if truncation event is next.

        If the file was truncated at current location, returns. Otherwise,
        returns False.

        Unlike `get_truncated()`, truncation event is not consumed, i.e.
        subsequent calls to `is_truncated()` would return the same value.
        """
        return self._truncated

    def __iter__(self):
        return self

    def __next__(self):
        if self.closed:
            raise ValueError("closed")
        while True:
            data = self.read(self.buffer_size)
            if len(data):
                return data
            elif self.get_truncated():
                return Truncated
            else:
                raise StopIteration

    def _check_truncated_pre_data(self):
        """do truncation checks before reading data"""
        if self.file is None:
            try:
                self.file = open(self.path, "rb")
                self._file_pos = 0  # only valid if self.file is not None
            except EnvironmentError:
                return True
        stat = os.fstat(self.file.fileno())
        if stat.st_size < self._file_pos:
            return True
        self._file_id = (stat.st_dev, stat.st_ino)

    def _check_truncated_post_data(self):
        """do truncation checks after reading data"""
        try:
            stat = os.stat(self.path)
        except EnvironmentError:
            # TODO when file is unlinked, maybe it's better to keep following
            # it, until a file with the same name is created again
            return Truncated
        if self._file_id != (stat.st_dev, stat.st_ino):
            return Truncated

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
        if self.file is not None:
            self.file.close()
        self.file = None
        self.closed = True
