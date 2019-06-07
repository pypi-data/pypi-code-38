# Copyright (c) 2019 Red Hat, Inc.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import io
import select

from oslo_log import log

import six

LOG = log.getLogger(__name__)


class ShellIOBase(io.IOBase):

    buffer_size = io.DEFAULT_BUFFER_SIZE

    def __init__(self, delegate, fd=None, buffer_size=None):
        super(ShellIOBase, self).__init__()
        self.delegate = delegate
        if buffer_size:
            self.buffer_size = int(buffer_size)
        if fd is None:
            fd = delegate.fileno()
        self.fd = fd
        self._data_chunks = []

    @property
    def data(self):
        chunks = self._data_chunks
        if not chunks:
            return None

        chunks_number = len(chunks)
        if chunks_number == 1:
            return chunks[0]

        # Use a zero-length object of chunk type to join chunks
        data = chunks[0][:0].join(chunks)
        self._data_chunks = chunks = [data]
        return data

    def __str__(self):
        data = self.data
        if not data:
            return ''

        if isinstance(data, six.string_types):
            return data

        return data.decode()

    def fileno(self):
        return self.fd

    def readable(self):
        return False

    def writable(self):
        return False

    def close(self):
        self.delegate.close()

    @property
    def closed(self):
        return self.delegate.closed

    def __bool__(self):
        for chunk in self._data_chunks:
            if chunk:
                return True
        return False


class ShellReadable(ShellIOBase):

    def readable(self):
        return True

    def read(self, size=None):
        size = size or self.buffer_size
        chunk = self.delegate.read(size)
        self._data_chunks.append(chunk)
        return chunk

    @property
    def read_ready(self):
        return (not self.closed and
                getattr(self.delegate, 'read_ready', False))


class ShellWritable(ShellIOBase):

    def writable(self):
        return True

    def write(self, chunk):
        witten_bytes = self.delegate.write(chunk)
        self._data_chunks.append(chunk)
        return witten_bytes

    @property
    def write_ready(self):
        return (not self.closed and
                getattr(self.delegate, 'write_ready', False))


class ShellStdin(ShellWritable):
    pass


class ShellStdout(ShellReadable):
    pass


class ShellStderr(ShellReadable):
    pass


def select_files(files, timeout, mode='rw'):
    # NOTE: in case there is no files that can be selected for given mode,
    # this function is going to behave like time.sleep()
    if timeout is None:
        message = "Invalid value for timeout: {!r}".format(timeout)
        raise ValueError(message)

    timeout = float(timeout)
    opened = select_opened_files(files)
    readable = writable = set()
    if 'r' in mode:
        readable = select_readable_files(opened)
    if 'w' in mode:
        writable = select_writable_files(opened)

    read_ready = select_read_ready_files(readable)
    write_ready = select_write_ready_files(writable)
    if not write_ready and not read_ready:
        if timeout > 0.:
            LOG.debug("Calling select with %d files and timeout %f",
                      len(opened), timeout)
        rlist, wlist, xlist = select.select(readable, writable, opened,
                                            timeout)
        read_ready = readable & set(rlist + xlist)
        write_ready = writable & set(wlist + xlist)

    return read_ready, write_ready


def select_opened_files(files):
    return {f for f in files if is_opened_file(f)}


def is_opened_file(f):
    return not getattr(f, 'closed', True)


def select_readable_files(files):
    return {f for f in files if is_readable_file(f)}


def is_readable_file(f):
    return f.readable()


def select_read_ready_files(files):
    return {f for f in files if f.read_ready}


def select_writable_files(files):
    return {f for f in files if is_writable_file(f)}


def is_writable_file(f):
    return f.writable()


def select_write_ready_files(files):
    return {f for f in files if f.write_ready}
