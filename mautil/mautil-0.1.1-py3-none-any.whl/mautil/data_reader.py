import numpy as np, time, logging
from queue import Queue, Empty
from threading import Thread
import multiprocessing as mp

from . import util

gl = globals()


class BasicBatchReader(object):
    def __init__(self, name, seed, batch_process_func=None):
        self.name = name
        self._rs = np.random.RandomState(seed)
        self._batch_process_func = batch_process_func


def create_data_reader(cls_name, name, seed, **kwargs):
    if cls_name in gl:
        cls = gl[cls_name]
    else:
        cls = util.get_class(cls_name)
    return cls(name, seed, **kwargs)


class BatchReader(BasicBatchReader):
    def __init__(self, name, seed, batch_process_func=None, process_mode='T', sleep_seconds=1, timeout=1, qsize=8, balanced_read=False, squeeze_seq=False, min_seq_len=-1, ordered=False,  **kwargs):
        """

        :param name:
        :param seed:
        :param process_mode: T for thread, P for subprocess, N for neither
        :param sleep_seconds:
        :param timeout:
        :param qsize:
        :param squeeze_seq: seqs will be squeezed to max_seq_len of batch
        """
        super(BatchReader, self).__init__(name, seed, batch_process_func)
        self._sleep_seconds = sleep_seconds
        self._process_mode = process_mode
        self._timeout = timeout
        self._qsize = qsize
        self._balanced_read = balanced_read
        self._do_squeeze_seq = squeeze_seq
        self._min_seq_len = min_seq_len
        self._ordered = ordered
        self.kwargs = kwargs

        if self._process_mode == 'P':
            self._queue = mp.Queue(self._qsize)
        elif self._process_mode == 'T':
            self._queue = Queue(self._qsize)


    def _squeeze_seq(self, batch, seq_keys):
        for seq_key, seq_len_key in seq_keys:
            seq_key = '_'.join(seq_len_key.split('_')[:-1])
            max_len = max(self._min_seq_len, np.max(batch[seq_len_key]))
            batch[seq_key] = batch[seq_key][:, :max_len]
        return batch

    def _get_seqs_keys(self, keys):
        seqs_len_keys = []
        seqs_keys = []
        for key in keys:
            if key.endswith('seqs_len'):
                seqs_len_keys.append(key)
                seqs_key = '_'.join(key.split('_')[:-1])
                seqs_keys.append(seqs_key)
        return seqs_keys, seqs_len_keys

    def get_batch(self, x, batch_size, y=None, shuffle=True, data_type='train'):
        seqs_keys, seqs_len_keys = self._get_seqs_keys(x.keys())

        get_batch_func = self._get_batch
        if self._balanced_read:
            get_batch_func = self._get_batch_balanced
        for batch in get_batch_func(x, batch_size, y, shuffle, data_type):
            if self._do_squeeze_seq is True:
                batch = self._squeeze_seq(batch, zip(seqs_keys, seqs_len_keys))

            if self._batch_process_func is not None:
                batch = self._batch_process_func(batch, data_type)
            yield batch

    def _get_batch(self, x, batch_size, y=None, shuffle=True, data_type='train'):
        for key in x:
            num = len(x[key])
            break
        inds = np.arange(num)
        if shuffle and not self._ordered:
            self._rs.shuffle(inds)
        num_batch = (num + batch_size -1)//batch_size
        batch_ids = np.arange(num_batch)
        if shuffle:
            self._rs.shuffle(batch_ids)

        for i in batch_ids:
            batch = {}
            batch_inds = inds[batch_size*i:min(batch_size*(i+1), num)]
            batch['batch_inds'] = batch_inds
            batch['batch_size'] = len(batch_inds)
            for key in x:
                batch[key] = x[key][batch_inds]

            if y is not None:
                for key in y:
                    batch[key] = y[key][batch_inds]
            yield batch

    def _gen_batch(self, x, batch_size, y, shuffle, data_type='train'):
        for i, batch in enumerate(self.get_batch(x, batch_size, y, shuffle=shuffle, data_type=data_type)):
            self._queue.put(batch, block=True)
        self._queue.put(None)

    def __call__(self, x, batch_size, y=None, shuffle=True, data_type='train'):
        """

        :param x: dict of array. key name endswith _seqs, _seqs_len were preserved for seqs data
        :param batch_size:
        :param y:
        :param shuffle:
        :param data_type:
        :return:
        """

        if self._process_mode == 'P':
            thread = mp.Process(target=self._gen_batch, args=[x, batch_size, y, shuffle, data_type])
        elif self._process_mode == 'T':
            thread = Thread(target=self._gen_batch, args=[x, batch_size, y, shuffle, data_type])
        if self._process_mode in ['T', 'P']:
            thread.daemon = True
            thread.start()
            time.sleep(self._sleep_seconds)
            logging.info('name:%s, get batch sleep %s seconds', self.name, self._sleep_seconds)
            while True:
                batch = self._queue.get(True, self._timeout)
                if batch is None:break;
                yield batch
        elif self._process_mode == 'N':
            for batch in self.get_batch(x, batch_size, y, shuffle=shuffle, data_type=data_type):
                yield batch


    def _get_batch_balanced(self, x, batch_size, y=None, shuffle=True, data_type='train'):
        """
        In some case data is imbalance
        """

        label_inds = []
        labels = np.unique(x['labels'])
        min_num =  np.inf
        for label in labels:
            label_ind = list(np.where(np.array(x['labels']) == label)[0])
            if shuffle and not self._ordered:
                self._rs.shuffle(label_ind)
            label_inds.append(label_ind)
            if len(label_ind) < min_num:
                min_num = len(label_ind)
        num_batch = (min_num + batch_size -1)//batch_size
        batch_ids = np.arange(num_batch)
        if shuffle:
            self._rs.shuffle(batch_ids)

        for i in batch_ids:
            batch = {}
            batch_inds = []
            for inds in label_inds:
                batch_inds += inds[batch_size*i:min(batch_size*(i+1), min_num)]
            batch['batch_inds'] = batch_inds
            batch['batch_size'] = len(batch_inds)
            for key in x:
                batch[key] = x[key][batch_inds]

            if y is not None:
                for key in y:
                    batch[key] = y[key][batch_inds]

            yield batch
