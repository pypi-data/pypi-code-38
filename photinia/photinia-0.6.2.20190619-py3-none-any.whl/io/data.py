#!/usr/bin/env python3

"""
@author: xi
@since: 2018-06-18
"""

import collections
import csv
import json
import queue
import random
import threading
import time

import numpy as np


class DataSource(object):

    def __init__(self, field_names):
        self._field_names = list(field_names)
        self._data_model = collections.namedtuple(
            'DataItem',
            field_names,
            rename=True  # here I set rename to "True" to prevent invalid field names, e.g., "_id" in mongodb
        )

    @property
    def field_names(self):
        return self._field_names

    def next(self):
        raise NotImplementedError()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


class MemorySource(DataSource):

    def __init__(self,
                 field_names,
                 docs,
                 dtype=None):
        super(MemorySource, self).__init__(field_names)

        self._columns = [list() for _ in range(len(self._field_names))]
        for doc in docs:
            for i, field_name in enumerate(self._field_names):
                self._columns[i].append(doc[field_name])
        self._columns = [
            np.array(column, dtype=dtype)
            for column in self._columns
        ]

        self._num_comp = len(self._field_names)
        if self._num_comp == 0:
            raise ValueError('At least 1 data object should be given.')
        self._size = len(self._columns[0])
        self._start = 0
        self._loop = 0

    @property
    def size(self):
        return self._size

    @property
    def start(self):
        return self._start

    @property
    def loop(self):
        return self._loop

    def next(self):
        if self._start >= self._size:
            self._start = 0
            self._loop += 1
            self.shuffle()
            raise StopIteration()
        row = self._data_model(
            *(column[self._start]
              for column in self._columns)
        )
        self._start += 1
        return row

    def next_batch(self, size=0):
        batch = self._next_batch(size)
        if size == 0:
            return batch
        real_size = len(batch[0])
        while real_size < size:
            batch1 = self._next_batch(size - real_size)
            batch = self._data_model(
                *(np.concatenate((batch[i], batch1[i]), 0)
                  for i in range(self._num_comp))
            )
            real_size = len(batch[0])
        return batch

    def _next_batch(self, size=0):
        if size <= 0:
            return self.all()
        if self._start == 0 and self._loop != 0:
            self.shuffle()
        end = self._start + size
        if end < self._size:
            batch = self._data_model(
                *(self._columns[i][self._start:end].copy()
                  for i in range(self._num_comp))
            )
            self._start += size
        else:
            batch = self._data_model(
                *(self._columns[i][self._start:].copy()
                  for i in range(self._num_comp))
            )
            self._start = 0
            self._loop += 1
        return batch

    def shuffle(self, num=3):
        perm = np.arange(self._size)
        for _ in range(num):
            np.random.shuffle(perm)
        for i in range(self._num_comp):
            self._columns[i] = self._columns[i][perm]
        return self

    def all(self):
        return self._columns


class CSVSource(DataSource):

    def __init__(self, field_names, fp, delimiter=','):
        super(CSVSource, self).__init__(field_names)

        reader = csv.DictReader(fp, delimiter=delimiter)
        self._iter = iter(reader)
        self._docs = list()

        self._memory_source = None

    def next(self):
        if self._memory_source is None:
            try:
                doc = next(self._iter)
            except StopIteration:
                self._memory_source = MemorySource(self._field_names, self._docs)
                self._iter = None
                self._docs = None
                raise StopIteration()
            self._docs.append(doc)
            # print('DEBUG: Fetch from file.')
            return self._data_model(
                *(doc[field_name]
                  for field_name in self._field_names)
            )
        # print('DEBUG: Fetch from memory.')
        return self._memory_source.next()


class JsonSource(DataSource):

    def __init__(self, field_names, fp):
        super(JsonSource, self).__init__(field_names)
        self._fp = fp
        self._docs = list()

        self._memory_source = None

    def next(self):
        if self._memory_source is None:
            try:
                doc = json.loads(next(self._fp))
            except StopIteration:
                self._memory_source = MemorySource(self._field_names, self._docs)
                self._fp = None
                self._docs = None
                raise StopIteration()
            self._docs.append(doc)
            # print('DEBUG: Fetch from file.')
            return self._data_model(
                *(doc[field_name]
                  for field_name in self._field_names)
            )
        # print('DEBUG: Fetch from memory.')
        return self._memory_source.next()


class MongoSource(DataSource):

    def __init__(self,
                 field_names,
                 coll,
                 filters=None,
                 random_order=False,
                 min_buffer_size=10,
                 max_buffer_size=1_000_000,
                 drop_prob=None):
        """Data source used to access MongoDB.

        Args:
            field_names (tuple|list): Field names of the data source.
            coll: MongoDB collection object.
            filters (dict): Filters which will be pass to MongoDB's find() operation.
            random_order (bool): If iterate the collections in random order.
                This is usually set to True when used as train set.
            min_buffer_size (int): Min size of the candidate buffer.
                Note that it will not return data items until the buffer reaches the min size.
                This mechanism is involved to increase the randomness of data iteration.
            max_buffer_size (int): Max size of the candidate buffer.
                This option will only take effect when random_order is True.

        """
        super(MongoSource, self).__init__(field_names)
        self._coll = coll
        self._filters = filters if filters is not None else {}
        self._projections = {field_name: 1 for field_name in field_names}
        self._random_order = random_order
        assert min_buffer_size < max_buffer_size
        self._min_buffer_size = min_buffer_size
        self._max_buffer_size = max_buffer_size
        self._drop_prob = drop_prob

        self._cursor = None
        self._buffer = list()

    def next(self):
        if self._random_order:
            doc = self._random_next()
        else:
            doc = self._normal_order()
        return self._data_model(
            *(doc[field_name]
              for field_name in self._field_names)
        )

    def _random_next(self):
        while True:
            #
            # fetch next ID from the database
            _id = None
            error = None
            for _ in range(3):
                try:
                    _id = self._next_id()
                    break
                except StopIteration as e:
                    raise e
                except Exception as e:
                    error = e
                    time.sleep(3)
                    continue

            #
            # add the ID from the buffer
            if _id is None:
                raise error
            if len(self._buffer) < self._max_buffer_size:
                self._buffer.append(_id)
            else:
                index = random.randint(0, self._max_buffer_size - 1)
                self._buffer[index] = _id

            if len(self._buffer) >= self._min_buffer_size:
                break

        #
        # get an ID from buffer randomly
        index = random.randint(0, len(self._buffer) - 1)
        _id = self._buffer[index]

        #
        # get the doc based on the ID
        doc = None
        error = None
        for _ in range(3):
            try:
                doc = self._coll.find_one({'_id': _id}, self._projections)
                break
            except Exception as e:
                error = e
                time.sleep(3)
                continue
        if doc is None:
            raise error

        return doc

    def _next_id(self):
        if self._cursor is None:
            self._cursor = self._coll.find(self._filters, {'_id': 1}, batch_size=1000)
        try:
            if self._drop_prob is None:
                doc = next(self._cursor)
            else:
                while True:
                    doc = next(self._cursor)
                    if random.uniform(0.0, 1.0) >= self._drop_prob:
                        break
        except Exception as e:
            #
            # the exception may be:
            # 1) StopIteration
            # 2) CursorTimeout
            self._cursor = None
            raise e
        return doc['_id']

    def _normal_order(self):
        doc = None
        error = None
        for _ in range(3):
            if self._cursor is None:
                self._cursor = self._coll.find(self._filters, self._projections)
            try:
                doc = next(self._cursor)
                break
            except StopIteration as e:
                self._cursor = None
                raise e
            except Exception as e:
                self._cursor = None
                error = e
                time.sleep(3)
                continue
        if doc is None:
            raise error

        return doc


class BatchSource(DataSource):

    def __init__(self,
                 input_source,
                 batch_size):
        """Return data item in batch.

        Args:
            input_source (DataSource): Data source to be wrapped.
            batch_size (int): Batch size.

        """
        self._input_source = input_source
        super(BatchSource, self).__init__(input_source.field_names)
        self._batch_size = batch_size

        self._cell_fns = collections.defaultdict(collections.deque)
        self._column_fns = collections.defaultdict(collections.deque)

        self._eof = False

    @property
    def batch_size(self):
        return self._batch_size

    def add_cell_fns(self, field_name, fns):
        if callable(fns):
            fns = [fns]
        elif not isinstance(fns, (list, tuple)):
            raise ValueError('fns should be callable or list(tuple) of callables.')
        if type(field_name) is not list:
            field_name = [field_name]
        for item in field_name:
            self._cell_fns[item] += fns

    def add_column_fns(self, field_name, fns):
        if callable(fns):
            fns = [fns]
        elif not isinstance(fns, (list, tuple)):
            raise ValueError('fns should be callable or list(tuple) of callables.')
        if type(field_name) is not list:
            field_name = [field_name]
        for item in field_name:
            self._column_fns[item] += fns

    def next(self):
        if self._eof:
            self._eof = False
            raise StopIteration()

        batch_doc = tuple(
            list() for _ in self._field_names
        )
        for i in range(self._batch_size):
            try:
                doc = self._next_one()
            except StopIteration as e:
                if i == 0:
                    raise e
                else:
                    self._eof = True
                    break
            for j, value in enumerate(doc):
                batch_doc[j].append(value)

        batch_doc = self._data_model(
            *(self._apply_column_fns(field_name, value)
              for field_name, value in zip(self._field_names, batch_doc))
        )
        return batch_doc

    def _next_one(self):
        doc = self._input_source.next()
        doc = tuple(
            self._apply_cell_fns(field_name, value)
            for field_name, value in zip(self._field_names, doc)
        )
        return doc

    def _apply_cell_fns(self, field_name, value):
        if field_name in self._cell_fns:
            for fn in self._cell_fns[field_name]:
                value = fn(value)
        return value

    def _apply_column_fns(self, field_name, column):
        if field_name in self._column_fns:
            for fn in self._column_fns[field_name]:
                column = fn(column)
        return column


class ThreadBufferedSource(DataSource):

    def __init__(self,
                 input_source,
                 buffer_size=1000,
                 auto_reload=False,
                 num_thread=0,
                 fn=None):
        """Preload data to a buffer in another thread.

        Args:
            input_source (DataSource): Data source to be wrapped.
            buffer_size (int): Buffer size.

        """
        self._input_source = input_source
        super(ThreadBufferedSource, self).__init__(input_source.field_names)
        if isinstance(buffer_size, int) and buffer_size > 0:
            self._buffer_size = buffer_size
        else:
            raise ValueError('buffer_size should be a positive integer.')
        self._auto_reload = auto_reload
        self._num_thread = num_thread
        self._fn = fn if callable(fn) else self._next
        #
        # Async Loading
        self._input_queue = queue.Queue(buffer_size)
        self._load_thread = None
        if num_thread > 0:
            self._output_queue = queue.Queue(buffer_size)
            self._input_notifies = [threading.Semaphore(0) for _ in range(num_thread)]
            self._output_notifies = [threading.Semaphore(0) for _ in range(num_thread)]
            self._input_notifies[-1].release()
            self._output_notifies[-1].release()
            self._notify_lock = threading.Semaphore(1)
            self._process_threads = [
                threading.Thread(target=self._process, args=(i,))
                for i in range(num_thread)
            ]
            for t in self._process_threads:
                t.setDaemon(True)
                t.start()
        else:
            self._output_queue = self._input_queue

    def next(self):
        if self._load_thread is None:
            self._load_thread = threading.Thread(target=self._load)
            self._load_thread.setDaemon(True)
            self._load_thread.start()

        row = self._output_queue.get(block=True)
        if isinstance(row, Exception):
            raise row
        return row

    def _load(self):
        """This method is executed in another thread!
        """
        while True:
            try:
                row = self._input_source.next()
                if self._num_thread <= 0:
                    row = self._fn(row)
                self._input_queue.put(row, block=True)
            except StopIteration as e:
                self._input_queue.put(e, block=True)
                if not self._auto_reload:
                    self._load_thread = None
                    break
            except Exception as e:
                #
                # If it's not StopIteration, that means there's an fatal error in the data source.
                # In this case, an exception should be raised and the program must be terminated.
                self._input_queue.put(e, block=True)
                self._load_thread = None
                break

    def _process(self, i):
        with self._notify_lock:
            input_notify_wait = self._input_notifies[i - 1]
            input_notify_release = self._input_notifies[i]
            output_notify_wait = self._output_notifies[i - 1]
            output_notify_release = self._output_notifies[i]

        while True:
            input_notify_wait.acquire()
            row = self._input_queue.get()
            input_notify_release.release()

            if not isinstance(row, Exception):
                row = self._fn(row)

            output_notify_wait.acquire()
            self._output_queue.put(row)
            output_notify_release.release()

    def _next(self, row):
        return row
