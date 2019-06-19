# Copyright (C) 2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import struct


class ChunkedFileReader(object):
    """A binary stream reader that gives seamless read access to Mercurial's
    bundle2 HG20 format which is partitioned for some reason at the file level
    into chunks of [4Bytes:<length>, <length>Bytes:<data>] as if it were
    encoding transport packets.

    args:
        file: rb file handle pre-aligned to the start of the chunked portion
        size_unpack_fmt: struct format string for unpacking the next chunk size
    """
    def __init__(self, file, size_unpack_fmt='>I'):
        self._file = file
        self._size_pattern = size_unpack_fmt
        self._size_bytes = struct.calcsize(size_unpack_fmt)
        self._bytes_per_chunk = self._chunk_size(True)
        self._chunk_bytes_left = self._bytes_per_chunk
        self._offset = self._file.tell()
        # find the file size
        self._file.seek(0, 2)  # seek to end
        self._size = self._file.tell()
        self._file.seek(self._offset, 0)  # seek back to original position

    def _chunk_size(self, first_time=False):
        """Unpack the next <determined_by_'size_unpack_fmt'> bytes from the
        file to get the next file chunk size.
        """
        size = struct.unpack(self._size_pattern,
                             self._file.read(self._size_bytes))[0]
        return size

    def size(self):
        """Returns the file size in bytes.
        """
        return self._size

    def read(self, bytes_to_read):
        """Return N bytes from the file as a single block.

        args:
            bytes_to_read: int number of bytes of content
        """
        return b''.join(self.read_iterator(bytes_to_read))

    def read_iterator(self, bytes_to_read):
        """Return a generator that yields N bytes from the file one file chunk
        at a time.

        args:
            bytes_to_read: int number of bytes of content
        """
        while bytes_to_read > self._chunk_bytes_left:
            yield self._file.read(self._chunk_bytes_left)
            bytes_to_read -= self._chunk_bytes_left
            self._chunk_bytes_left = self._chunk_size()
        self._chunk_bytes_left -= bytes_to_read
        yield self._file.read(bytes_to_read)

    def seek(self, new_pos=None, from_current=False):
        """Wraps the underlying file seek, additionally updating the
        chunk_bytes_left counter appropriately so that we can start reading
        from the new location.

        args:

            new_pos: new cursor byte position
            from_current: if True, it treats new_pos as an offset from the
                current cursor position, bypassing any chunk boundaries as if
                they weren't there. This should give the same end position as a
                read except without the reading data part.
        """
        if from_current:
            new_pos = new_pos or 0              # None -> current
            if new_pos <= self._chunk_bytes_left:
                new_pos += self._file.tell()
            else:
                new_pos += (
                    self._file.tell()
                    + self._size_bytes
                    + (
                        (
                            (new_pos - self._chunk_bytes_left - 1)  # aliasing
                            // self._bytes_per_chunk
                        )
                        * self._size_bytes
                    )
                )
        else:
            new_pos = new_pos or self._offset   # None -> start position

        self._chunk_bytes_left = self._bytes_per_chunk - (
            (new_pos - self._offset)
            % (self._bytes_per_chunk + self._size_bytes)
        )
        self._file.seek(new_pos)

    def __getattr__(self, item):
        """Forward other calls to the underlying file object.
        """
        return getattr(self._file, item)
