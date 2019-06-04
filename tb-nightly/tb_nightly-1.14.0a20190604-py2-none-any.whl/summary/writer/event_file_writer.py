# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Writes events to disk in a logdir."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import socket
import threading
import time

import six

from tensorboard.compat.proto import event_pb2
from tensorboard.summary.writer.record_writer import RecordWriter


class AtomicCounter(object):
  def __init__(self, initial_value):
    self._value = initial_value
    self._lock = threading.Lock()

  def get(self):
    with self._lock:
      try:
        return self._value
      finally:
        self._value += 1


_global_uid = AtomicCounter(0)


class EventFileWriter(object):
    """Writes `Event` protocol buffers to an event file.

    The `EventFileWriter` class creates an event file in the specified directory,
    and asynchronously writes Event protocol buffers to the file. The Event file
    is encoded using the tfrecord format, which is similar to RecordIO.
    """

    def __init__(self, logdir, max_queue_size=10, flush_secs=120, filename_suffix=''):
        """Creates a `EventFileWriter` and an event file to write to.

        On construction the summary writer creates a new event file in `logdir`.
        This event file will contain `Event` protocol buffers, which are written to
        disk via the add_event method.
        The other arguments to the constructor control the asynchronous writes to
        the event file:

        Args:
          logdir: A string. Directory where event file will be written.
          max_queue_size: Integer. Size of the queue for pending events and summaries.
          flush_secs: Number. How often, in seconds, to flush the
            pending events and summaries to disk.
        """
        self._logdir = logdir
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        self._file_name = os.path.join(logdir, "events.out.tfevents.%010d.%s.%s.%s" %
            (time.time(), socket.gethostname(), os.getpid(), _global_uid.get())) + filename_suffix  # noqa E128
        self._general_file_writer = open(self._file_name, 'wb')
        self._async_writer = _AsyncWriter(RecordWriter(self._general_file_writer), max_queue_size, flush_secs)

        # Initialize an event instance.
        _event = event_pb2.Event(wall_time=time.time(), file_version='brain.Event:2')
        self.add_event(_event)
        self.flush()

    def get_logdir(self):
        """Returns the directory where event file will be written."""
        return self._logdir

    def add_event(self, event):
        """Adds an event to the event file.

        Args:
          event: An `Event` protocol buffer.
        """
        if not isinstance(event, event_pb2.Event):
            raise TypeError("Expected an event_pb2.Event proto, "
                            " but got %s" % type(event))
        self._async_writer.write(event.SerializeToString())

    def flush(self):
        """Flushes the event file to disk.

        Call this method to make sure that all pending events have been written to
        disk.
        """
        self._async_writer.flush()

    def close(self):
        """Performs a final flush of the event file to disk, stops the
        write/flush worker and closes the file. Call this method when you do not
        need the summary writer anymore.
        """
        self._async_writer.close()


class _AsyncWriter(object):
    '''Writes bytes to a file.'''

    def __init__(self, record_writer, max_queue_size=20, flush_secs=120):
        """Writes bytes to a file asynchronously.
        An instance of this class holds a queue to keep the incoming data temporarily.
        Data passed to the `write` function will be put to the queue and the function
        returns immediately. This class also maintains a thread to write data in the
        queue to disk. The first initialization parameter is an instance of
        `tensorboard.summary.record_writer` which computes the CRC checksum and then write
        the combined result to the disk. So we use an async approach to improve performance.

        Args:
            record_writer: A RecordWriter instance
            max_queue_size: Integer. Size of the queue for pending bytestrings.
            flush_secs: Number. How often, in seconds, to flush the
                pending bytestrings to disk.
        """
        self._writer = record_writer
        self._closed = False
        self._byte_queue = six.moves.queue.Queue(max_queue_size)
        self._worker = _AsyncWriterThread(self._byte_queue, self._writer, flush_secs)
        self._lock = threading.Lock()
        self._worker.start()

    def write(self, bytestring):
        '''Enqueue the given bytes to be written asychronously'''
        with self._lock:
            if self._closed:
                raise IOError('Writer is closed')
            self._byte_queue.put(bytestring)

    def flush(self):
        '''Write all the enqueued bytestring before this flush call to disk.
        Block until all the above bytestring are written.
        '''
        with self._lock:
            if self._closed:
                raise IOError('Writer is closed')
            self._byte_queue.join()
            self._writer.flush()

    def close(self):
        '''Closes the underlying writer, flushing any pending writes first.'''
        if not self._closed:
            with self._lock:
                if not self._closed:
                    self._closed = True
                    self._worker.stop()
                    self._writer.flush()
                    self._writer.close()


class _AsyncWriterThread(threading.Thread):
    """Thread that processes asynchronous writes for _AsyncWriter."""

    def __init__(self, queue, record_writer, flush_secs):
        """Creates an _AsyncWriterThread.
        Args:
          queue: A Queue from which to dequeue data.
          record_writer: An instance of record_writer writer.
          flush_secs: How often, in seconds, to flush the
            pending file to disk.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self._queue = queue
        self._record_writer = record_writer
        self._flush_secs = flush_secs
        # The first data will be flushed immediately.
        self._next_flush_time = 0
        self._has_pending_data = False
        self._shutdown_signal = object()

    def stop(self):
        self._queue.put(self._shutdown_signal)
        self.join()

    def run(self):
        # Here wait on the queue until an data appears, or till the next
        # time to flush the writer, whichever is earlier. If we have an
        # data, write it. If not, an empty queue exception will be raised
        # and we can proceed to flush the writer.
        while True:
            now = time.time()
            queue_wait_duration = self._next_flush_time - now
            data = None
            try:
                if queue_wait_duration > 0:
                    data = self._queue.get(True, queue_wait_duration)
                else:
                    data = self._queue.get(False)

                if data is self._shutdown_signal:
                    return
                self._record_writer.write(data)
                self._has_pending_data = True
            except six.moves.queue.Empty:
                pass
            finally:
                if data:
                    self._queue.task_done()

            now = time.time()
            if now > self._next_flush_time:
                if self._has_pending_data:
                    # Small optimization - if there are no pending data,
                    # there's no need to flush, since each flush can be
                    # expensive (e.g. uploading a new file to a server).
                    self._record_writer.flush()
                    self._has_pending_data = False
                # Do it again in flush_secs.
                self._next_flush_time = now + self._flush_secs
