# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#
"""
Utilities for wrapping IO streams. These are used internally by
fresco when parsing wsgi request input streams.
"""
from __future__ import absolute_import

from io import BytesIO, IOBase

from collections import deque
from tempfile import TemporaryFile
from shutil import copyfileobj


class ReadlinesMixin(object):
    """
    Mixin that defines readlines and the iterator interface in terms of
    underlying readline method.
    """

    def readlines(self, sizehint=0):
        size = 0
        lines = []
        for line in iter(self.readline, b''):
            lines.append(line)
            size += len(line)
            if 0 < sizehint <= size:
                break
        return lines

    def __iter__(self):
        return self

    def next(self):
        return self.readline()

    def __next__(self):
        return self.readline()


class Reader(IOBase):

    def readable(self):
        return True


class Seeker(IOBase):

    def seekable(self):
        return True


class Writer(IOBase):

    def writable(self):
        return True


class PutbackInput(Reader, ReadlinesMixin):
    r"""
    Wrap a file-like object to allow data read to be returned to the buffer.

    Only supports serial read-access, ie no seek or write methods.

    Example::

        >>> from io import BytesIO
        >>> s = BytesIO(b"the rain in spain\nfalls mainly\non the plain\n")
        >>> p = PutbackInput(s)
        >>> line = p.readline()
        >>> line
        'the rain in spain\n'
        >>> p.putback(line)
        >>> p.readline()
        'the rain in spain\n'
    """

    def __init__(self, raw):
        """
        Initialize a ``PutbackInput`` object from raw input stream ``raw``.
        """
        self._raw = raw
        self._putback = deque()

    def read(self, size=-1):
        """
        Read and return up to ``size`` bytes.
        """
        if size < 0:
            result = b''.join(self._putback) + self._raw.read()
            self._putback.clear()
            return result

        buf = []
        remaining = size
        while remaining > 0 and self._putback:
            chunk = self._putback.popleft()
            excess = len(chunk) - remaining
            if excess > 0:
                chunk, p = chunk[:-excess], chunk[-excess:]
                self.putback(p)

            buf.append(chunk)
            remaining -= len(chunk)

        if remaining > 0:
            buf.append(self._raw.read(remaining))

        return b''.join(buf)

    def readline(self, size=-1):
        """
        Read a single line of up to ``size`` bytes.
        """

        remaining = size
        buf = []
        while self._putback and (size < 0 or remaining > 0):
            chunk = self._putback.popleft()

            if size > 0:
                excess = len(chunk) - remaining
                if excess > 0:
                    chunk, p = chunk[:-excess], chunk[-excess:]
                    self.putback(p)

            pos = chunk.find(b'\n')
            if pos >= 0:
                chunk, p = chunk[:(pos + 1)], chunk[(pos + 1):]
                self.putback(p)
                buf.append(chunk)
                return b''.join(buf)

            buf.append(chunk)
            remaining -= len(chunk)

        if size > 0:
            buf.append(self._raw.readline(remaining))
        else:
            buf.append(self._raw.readline())

        return b''.join(buf)

    def putback(self, data):
        """
        Put ``data`` back into the stream
        """
        self._putback.appendleft(data)

    def peek(self, size):
        """
        Peek ahead ``size`` bytes from the stream without consuming any data
        """
        peeked = self.read(size)
        self.putback(peeked)
        return peeked


class SizeLimitedInput(Reader, Seeker, ReadlinesMixin):
    r"""\
    Wrap an IO object to prevent reading beyond ``length`` bytes.

    Example::

        >>> from io import BytesIO
        >>> s = BytesIO(b"the rain in spain\nfalls mainly\non the plain\n")
        >>> s = SizeLimitedInput(s, 24)
        >>> len(s.read())
        24
        >>> s.seek(0)
        0L
        >>> s.read()
        'the rain in spain\nfalls '
        >>> s.seek(0)
        0L
        >>> s.readline()
        'the rain in spain\n'
        >>> s.readline()
        'falls '
    """

    def __init__(self, raw, length):
        self._raw = raw
        self.length = length
        self.pos = 0

    def check_available(self, requested):
        """\
        Return the minimum of ``requested`` and the number of bytes available
        in the stream. If ``requested`` is negative, return the number of bytes
        available in the stream.
        """
        if requested < 0:
            return self.length - self.pos
        else:
            return min(self.length - self.pos, requested)

    def tell(self):
        """\
        Return the position of the file pointer in the stream.
        """
        return self.pos

    def seek(self, pos, whence=0):
        """\
        Seek to position ``pos``. This is a wrapper for the underlying IO's
        ``seek`` method.
        """
        self._raw.seek(pos, whence)
        self.pos = self._raw.tell()
        return self.pos

    def read(self, size=-1):
        """\
        Return up to ``size`` bytes from the input stream.
        """
        size = self.check_available(size)
        result = self._raw.read(size)
        self.pos += len(result)
        return result

    def readline(self, size=-1):
        """\
        Read a single line of up to ``size`` bytes from the input stream.
        """
        size = self.check_available(size)
        result = self._raw.readline(self.check_available(size))
        self.pos += len(result)
        return result


class DelimitedInput(Reader, ReadlinesMixin):
    r"""\
    Wrap a PutbackInput to read as far as a delimiter (after which subsequent
    reads will return empty strings, as if EOF was reached)

    Examples::

        >>> from io import BytesIO
        >>> s = BytesIO(b'one--two--three')
        >>> p = PutbackInput(s)
        >>> DelimitedInput(p, b'--').read()
        'one'
        >>> DelimitedInput(p, b'--').read()
        'two'
        >>> DelimitedInput(p, b'--').read()
        'three'
        >>> DelimitedInput(p, b'--').read()
        ''

    """

    def __init__(self, raw, delimiter, consume_delimiter=True):
        """\
        Initialize an instance of ``DelimitedInput``.
        """

        if not getattr(raw, 'putback', None):
            raise TypeError("Need an instance of PutbackInput")

        self._raw = raw
        self.delimiter = delimiter
        self.consume_delimiter = consume_delimiter
        self.delimiter_found = False
        self.delimiter_len = len(delimiter)

    def read(self, size=-1):
        """
        Return up to ``size`` bytes of data from the stream until EOF or
        ``delimiter`` is reached.
        """
        if self.delimiter_found:
            return b''
        MAX_BLOCK_SIZE = 8 * 1024
        if size == -1:
            return ''.join(iter(lambda: self.read(MAX_BLOCK_SIZE), b''))

        data = self._raw.read(size + self.delimiter_len)
        pos = data.find(self.delimiter)
        if pos >= 0:
            if self.consume_delimiter:
                putback = data[pos + self.delimiter_len:]
            else:
                putback = data[pos:]
            self.delimiter_found = True
            self._raw.putback(putback)
            return data[:pos]

        elif len(data) == size + self.delimiter_len:
            self._raw.putback(data[-self.delimiter_len:])
            return data[:-self.delimiter_len]

        else:
            return data

    def readline(self, size=-1):
        """
        Read a single line of up to ``size`` bytes from the input stream, or up
        to ``delimiter`` if this is encountered before a complete line is read.
        """

        if self.delimiter_found:
            return b''
        line = self._raw.readline(size)
        extra = self._raw.read(len(self.delimiter))
        if self.delimiter not in line + extra:
            self._raw.putback(extra)
            return line

        data = line + extra
        pos = data.find(self.delimiter)
        if pos >= 0:
            if self.consume_delimiter:
                putback = data[pos + len(self.delimiter):]
            else:
                putback = data[pos:]
            self.delimiter_found = True
            self._raw.putback(putback)
            return data[:pos]
        elif len(data) == size + len(self.delimiter):
            self._raw.putback(data[-len(self.delimiter):])
            return data[:-len(self.delimiter)]
        else:
            return data

    def close(self):
        """
        Don't close the underlying stream unless it has been fully consumed
        """


class ExpandableOutput(Reader, Writer, Seeker):
    """
    Write-only output object.

    Will store data in a BytesIO, until more than ``bufsize`` bytes are
    written, at which point it will switch to storing data in a real file
    object.
    """

    def __init__(self, bufsize=16384):
        """
        Initialize an ``ExpandableOutput`` instance.
        """
        self._raw = BytesIO()
        self.bufsize = bufsize
        self.write = self.write_stringio
        self.exceeded_bufsize = False

    def getstorage(self):
        """\
        Return the underlying stream (either a BytesIO or file object)
        """
        return self._raw

    def seek(self, pos, whence=0):
        return self._raw.seek(pos, whence)

    def tell(self):
        return self._raw.tell()

    def read(self, size=-1):
        return self._raw.read(size)

    def readline(self, size=-1):
        return self._raw.read(size)

    def write_stringio(self, data):
        """
        ``write``, optimized for the BytesIO backend.
        """
        if isinstance(self._raw, BytesIO) \
           and self._raw.tell() + len(data) > self.bufsize:
            self.switch_to_file_storage()
            return self.write_file(data)
        return self._raw.write(data)

    def write_file(self, data):
        """
        ``write``, optimized for the TemporaryFile backend
        """
        return self._raw.write(data)

    def switch_to_file_storage(self):
        """
        Switch the storage backend to an instance of ``TemporaryFile``.
        """
        self.exceeded_bufsize = True
        oldio = self._raw
        try:
            self._raw.seek(0)
            self._raw = TemporaryFile()
            copyfileobj(oldio, self._raw)
        finally:
            oldio.close()
        self.write = self.write_file

    def __enter__(self):
        """
        Support for context manager ``__enter__``/``__exit__`` blocks
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        Support for context manager ``__enter__``/``__exit__`` blocks
        """
        self._raw.close()
        # propagate exceptions
        return False
