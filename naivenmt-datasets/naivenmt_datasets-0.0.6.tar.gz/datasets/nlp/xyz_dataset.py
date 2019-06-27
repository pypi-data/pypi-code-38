import logging

import tensorflow as tf
from tensorflow.python.ops import lookup_ops


class XYZBaseDataset:

    def __init__(self, config=None, logger_name=None):
        """Init.

        Args:
            config: A python dict, custom configurations
            logger_name: A str, used to get logger
        """
        self.logger = logging.getLogger(logger_name)

        default_config = self._default_config()
        if config:
            default_config.update(config)
        self.config = default_config
        self.logger.info('dataset config is: %s\n', self.config)

        # convert string tokens to integer
        if not self.config['x_vocab_file']:
            raise ValueError('x_vocab_file must be provided, used to build lookup table.')
        x_str2id = lookup_ops.index_table_from_file(
            self.config['x_vocab_file'], default_value=self.config['unk_id'])
        if self.config['share_vocab_file']:
            y_str2id = x_str2id
        else:
            if not self.config['y_vocab_file']:
                raise ValueError('y_vocab_file must be provided, used to build lookup table.')
            y_str2id = lookup_ops.index_table_from_file(
                self.config['y_vocab_file'], default_value=self.config['unk_id'])
        self.x_str2id = x_str2id
        self.y_str2id = y_str2id

    def _build_dataset_from_files(self, files):
        if isinstance(files, str):
            self.logger.info('build dataset from a single file.')
            dataset = tf.data.TextLineDataset(files).skip(self.config.get('skip_count', 0))
        elif isinstance(files, list):
            self.logger.info('build dataset from a list of files.')
            dataset = tf.data.Dataset.from_tensor_slices(files)
            dataset = dataset.flat_map(lambda x: tf.data.TextLineDataset(x).skip(self.config.get('skip_count', 0)))
        else:
            raise ValueError('Argument `files` must be a `str` or a `list`.')
        return dataset

    def _build_dataset(self, dataset, mode='TRAIN'):
        """Build dataset for TRAIN and EVAL mode.

        Args:
            dataset: An instance of tf.data.Dataset
            mode: A str, one of ['TRAIN', 'EVAL']

        Returns:
            An instance of tf.data.Dataset
        """
        assert mode in {'TRAIN', 'EVAL'}

        # normalize labels in categorical or binary form
        @tf.function
        def _normalize_label_fn(x):
            if tf.equal(x, '0 1'):
                return tf.constant(1, dtype=tf.int64)
            if tf.equal(x, '1'):
                return tf.constant(1, dtype=tf.int64)
            return tf.constant(0, dtype=tf.int64)

        # split sequences
        dataset = dataset.map(
            lambda x, y, z: (
                tf.strings.split([x], sep=self.config['sequence_sep']).values,
                tf.strings.split([y], sep=self.config['sequence_sep']).values,
                _normalize_label_fn(z)),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        dataset = dataset.filter(lambda x, y, z: tf.logical_and(tf.size(x) > 0, tf.size(y) > 0))

        # filter sequence that are too long
        x_max_len = self.config.get('x_max_len', -1)
        if x_max_len > 0:
            dataset = dataset.filter(lambda x, y, z: tf.size(x) <= x_max_len)
        y_max_len = self.config.get('y_max_len', -1)
        if y_max_len > 0:
            dataset = dataset.filter(lambda x, y, z: tf.size(y) <= y_max_len)
        dataset = dataset.map(
            lambda x, y, z: (self.x_str2id.lookup(x), self.y_str2id.lookup(y), z),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        # padding and batching
        batch_size = self.config['train_batch_size'] if mode == 'TRAIN' else self.config['eval_batch_size']
        unk_id = tf.constant(self.config['unk_id'], dtype=tf.int64)
        x_padded_shape = x_max_len if x_max_len > 0 else None
        y_padded_shape = y_max_len if y_max_len > 0 else None
        dataset = dataset.padded_batch(
            batch_size=batch_size,
            padded_shapes=([x_padded_shape], [y_padded_shape], []),
            padding_values=(unk_id, unk_id, unk_id)
        ).prefetch(self.config['prefetch_size'])

        # in general, x and y are two inputs of the model, so zip them.
        dataset = dataset.map(
            lambda x, y, z: ((x, y), z),
            num_parallel_calls=self.config['num_parallel_calls'])
        return dataset

    def _build_predict_dataset(self, dataset):
        dataset = dataset.map(
            lambda x, y: (
                tf.strings.split([x], sep=self.config['sequence_sep']).values,
                tf.strings.split([y], sep=self.config['sequence_sep']).values),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        dataset = dataset.filter(lambda x, y: tf.logical_and(tf.size(x) > 0, tf.size(y) > 0))

        dataset = dataset.map(
            lambda x, y: (self.x_str2id.lookup(x), self.y_str2id.lookup(y)),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        unk_id = tf.constant(self.config['unk_id'], dtype=tf.int64)
        dataset = dataset.padded_batch(
            batch_size=self.config['predict_batch_size'],
            padded_shapes=(self.config['x_max_len'], self.config['y_max_len']),
            padding_values=(unk_id, unk_id)
        )

        dataset = dataset.map(lambda x, y: ((x, y),))
        return dataset

    def _default_config(self):
        config = {
            'train_batch_size': 32,
            'eval_batch_size': 32,
            'predict_batch_size': 32,
            'skip_count': 0,
            'buffer_size': 1000000,  # greater than total number of samples.
            'prefetch_size': tf.data.experimental.AUTOTUNE,  # samples prefetch buffer size
            'seed': None,
            'reshuffle_each_iteration': True,
            'line_sep': '@',
            'sequence_sep': ' ',
            'num_parallel_calls': 4,
            'x_vocab_file': None,
            'y_vocab_file': None,
            'share_vocab_file': False,
            'unk_id': 0,
            'x_max_len': 100,
            'y_max_len': 100,
        }
        self.logger.debug('default config: %s\n', config)
        return config


class XYZSameFileDataset(XYZBaseDataset):
    """Build dataset from files.
    Each line of file(s) is in form: x_SEP_y_SEP_z, where x and y are sequence, z is label."""

    def _process_train_and_eval_dataset(self, dataset):
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])

        # split line
        dataset = dataset.map(lambda x: tf.strings.split([x], sep=self.config['line_sep']).values,
                              num_parallel_calls=self.config['num_parallel_calls'])

        # filter lines which are not formed as x_SEP_y_SEP_z
        dataset = dataset.filter(lambda x: tf.equal(tf.size(x), 3))

        # convert list to tuple(x, y, z)
        dataset = dataset.map(lambda x: (x[0], x[1], x[2]),
                              num_parallel_calls=self.config['num_parallel_calls'])
        return dataset

    def build_train_dataset(self, train_files):
        dataset = self._build_dataset_from_files(train_files)
        dataset = self._process_train_and_eval_dataset(dataset)
        return self._build_dataset(dataset, 'TRAIN')

    def build_eval_dataset(self, eval_files):
        dataset = self._build_dataset_from_files(eval_files)
        dataset = self._process_train_and_eval_dataset(dataset)
        return self._build_dataset(dataset, 'EVAL')

    def build_predict_dataset(self, predict_files):
        dataset = self._build_dataset_from_files(predict_files)
        dataset = dataset.map(lambda x: tf.strings.split([x], sep=self.config['line_sep']).values,
                              num_parallel_calls=self.config['num_parallel_calls'])
        dataset = dataset.filter(lambda x: tf.equal(tf.size(x), 3))  # assume predict file contains label
        dataset = dataset.map(lambda x: (x[0], x[1]))  # take x and y only!
        return self._build_predict_dataset(dataset)


class XYZSeparateFileDataset(XYZBaseDataset):

    def build_train_dataset(self, x_files, y_files, z_files):
        x_dataset = self._build_dataset_from_files(x_files)
        y_dataset = self._build_dataset_from_files(y_files)
        z_dataset = self._build_dataset_from_files(z_files)
        dataset = tf.data.Dataset.zip((x_dataset, y_dataset, z_dataset))
        # shuffle
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])
        return self._build_dataset(dataset, mode='TRAIN')

    def build_eval_dataset(self, x_files, y_files, z_files):
        x_dataset = self._build_dataset_from_files(x_files)
        y_dataset = self._build_dataset_from_files(y_files)
        z_dataset = self._build_dataset_from_files(z_files)
        dataset = tf.data.Dataset.zip((x_dataset, y_dataset, z_dataset))
        # shuffle
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])
        return self._build_dataset(dataset, mode='EVAL')

    def build_predict_dataset(self, x_files, y_files):
        x_dataset = self._build_dataset_from_files(x_files)
        y_dataset = self._build_dataset_from_files(y_files)
        dataset = tf.data.Dataset.zip((x_dataset, y_dataset))
        return self._build_predict_dataset(dataset)
