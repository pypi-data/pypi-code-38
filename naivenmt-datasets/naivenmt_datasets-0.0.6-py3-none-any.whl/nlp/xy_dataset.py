import logging

import tensorflow as tf
from tensorflow.python.ops import lookup_ops


class XYBaseDataset:
    """Build dataset for two sequences, used typically in seq2seq models, where x is feature and y is label."""

    def __init__(self, config=None, logger_name=None):
        self.logger = logging.getLogger(logger_name)
        default_config = self._default_config()
        if config:
            default_config.update(config)
        self.config = default_config

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
        assert mode in {'TRAIN', 'EVAL'}

        dataset = dataset.map(
            lambda x, y: (
                tf.strings.split([x], sep=self.config['sequence_sep']).values,
                tf.strings.split([y], sep=self.config['sequence_sep']).values,),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        # filter empty sequences
        dataset = dataset.filter(lambda x, y: tf.logical_and(tf.size(x) > 0, tf.size(y) > 0))

        # length filter
        x_max_len = self.config.get('x_max_len', -1)
        if x_max_len > 0:
            dataset = dataset.filter(lambda x, y: tf.size(x) <= x_max_len)
        y_max_len = self.config.get('y_max_len', -1)
        if y_max_len > 0:
            dataset = dataset.filter(lambda x, y: tf.size(y) <= y_max_len)

        dataset = dataset.map(
            lambda x, y: (self.x_str2id.lookup(x), self.y_str2id.lookup(y)),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        # add sos and eos
        sos_id = tf.constant(self.config['sos_id'], dtype=tf.int64)
        eos_id = tf.constant(self.config['eos_id'], dtype=tf.int64)
        unk_id = tf.constant(self.config['unk_id'], dtype=tf.int64)
        if self.config['add_sos']:
            dataset = dataset.map(
                lambda x, y: (tf.concat(([sos_id], x), axis=0), tf.concat(([sos_id], y), axis=0)),
                num_parallel_calls=self.config['num_parallel_calls']
            ).prefetch(self.config['prefetch_size'])
        if self.config['add_eos']:
            dataset = dataset.map(
                lambda x, y: (tf.concat((x, [eos_id]), axis=0), tf.concat((y, [eos_id]), axis=0)),
                num_parallel_calls=self.config['num_parallel_calls']
            ).prefetch(self.config['prefetch_size'])

        # padding and batching
        batch_size = self.config['train_batch_size'] if mode == 'TRAIN' else self.config['eval_batch_size']
        padding_value = eos_id if self.config['add_eos'] else unk_id
        x_padded_shape = x_max_len if x_max_len > 0 else None
        y_padded_shape = y_max_len if y_max_len > 0 else None
        dataset = dataset.padded_batch(
            batch_size=batch_size,
            padding_values=(padding_value, padding_value),
            padded_shapes=([x_padded_shape], [y_padded_shape])
        )

        return dataset

    def _build_predict_dataset(self, dataset):
        dataset = dataset.map(
            lambda x: tf.strings.split([x], sep=self.config['sequence_sep']).values,
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        dataset = dataset.filter(lambda x: tf.size(x) > 0)

        dataset = dataset.map(
            lambda x: self.x_str2id.lookup(x),
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        sos_id = tf.constant(self.config['sos_id'], dtype=tf.int64)
        eos_id = tf.constant(self.config['eos_id'], dtype=tf.int64)
        unk_id = tf.constant(self.config['unk_id'], dtype=tf.int64)
        if self.config['add_sos']:
            dataset = dataset.map(lambda x: tf.concat(([sos_id], x), axis=0),
                                  num_parallel_calls=self.config['num_parallel_calls'])
        if self.config['add_eos']:
            dataset = dataset.map(lambda x: tf.concat((x, [eos_id]), axis=0),
                                  num_parallel_calls=self.config['num_parallel_calls'])

        padding_value = eos_id if self.config['add_eos'] else unk_id
        x_max_len = self.config.get('x_max_len', -1)
        padded_shape = x_max_len if x_max_len > 0 else None
        dataset = dataset.padded_batch(
            batch_size=self.config['predict_batch_size'],
            padding_values=padding_value,
            padded_shapes=padded_shape
        )
        return dataset

    def _default_config(self):
        config = {
            'buffer_size': 1000000,  # greater than total number of samples
            'seed': None,
            'reshuffle_each_iteration': True,
            'num_parallel_calls': 4,
            'prefetch_size': tf.data.experimental.AUTOTUNE,
            'line_sep': '@',
            'sequence_sep': ' ',
            'x_vocab_file': None,
            'y_vocab_file': None,
            'share_vocab_file': False,
            'x_max_len': -1,
            'y_max_len': -1,
            'add_sos': True,  # add sos to x and y or not
            'add_eos': True,  # add eos to x and y or not
            'unk_id': 0,  # unk is the first token in vocab
            'sos_id': 1,  # sos is second token in vocab
            'eos_id': 2,  # eos is third token in vocab
            'train_batch_size': 32,
            'eval_batch_size': 32,
            'predict_batch_size': 32,
        }
        return config


class XYSameFileDataset(XYBaseDataset):
    """Build dataset from files.
    Each line of file(s) is in form: x_SEP_y, where x and y are sequence. Used typically in seq2seq models."""

    def _process_train_and_eval_dataset(self, dataset):
        """Process dataset for traning or evaluation."""
        # shuffle dataset
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])

        # split line
        dataset = dataset.map(lambda x: tf.strings.split([x], sep=self.config['line_sep']).values,
                              num_parallel_calls=self.config['num_parallel_calls'])

        # filter lines which are not formed as x_SEP_y_SEP_z
        dataset = dataset.filter(lambda x: tf.equal(tf.size(x), 2))

        # convert list to tuple(x, y, z)
        dataset = dataset.map(lambda x: (x[0], x[1]),
                              num_parallel_calls=self.config['num_parallel_calls'])
        return dataset

    def build_train_dataset(self, train_files):
        """Build dataset for training.

        Args:
            train_files: A file path or a list of file paths

        Returns:
            A tf.data.Dataset instance.
        """
        dataset = self._build_dataset_from_files(train_files)
        dataset = self._process_train_and_eval_dataset(dataset)
        return self._build_dataset(dataset, mode='TRAIN')

    def build_eval_dataset(self, eval_files):
        """Build dataset for evaluating.

        Args:
            eval_files: A file path or a list of file paths

        Returns:
            A tf.data.Dataset instance.
        """
        dataset = self._build_dataset_from_files(eval_files)
        dataset = self._process_train_and_eval_dataset(dataset)
        return self._build_dataset(dataset, mode='EVAL')

    def build_predict_dataset(self, predict_files):
        """Build dataset for predicting.

        Args:
            predict_files: A file path or a list of file paths

        Returns:
            A tf.data.Dataset instance.
        """
        dataset = self._build_dataset_from_files(predict_files)
        dataset = dataset.map(
            lambda x: tf.strings.split([x], sep=self.config['line_sep']).values,
            num_parallel_calls=self.config['num_parallel_calls']
        ).prefetch(self.config['prefetch_size'])

        dataset = dataset.filter(lambda x: tf.equal(tf.size(x), 2))  # assume predict files contains label
        dataset = dataset.map(lambda x: x[0])  # toke x only!

        return self._build_predict_dataset(dataset)


class XYSeparateFileDataset(XYBaseDataset):
    """Build dataset from files.
    Features and labels are saved in separate files, each line from features and labels files is zipped together."""

    def build_train_dataset(self, x_files, y_files):
        """Build dataset for training.

        Args:
            x_files: A file path or a list of file paths, feature files in common.
            y_files: A file path or a list of file paths, label file in common.

        Returns:
            A tf.data.Dataset instance.
        """
        feature_dataset = self._build_dataset_from_files(x_files)
        label_dataset = self._build_dataset_from_files(y_files)
        dataset = tf.data.Dataset.zip((feature_dataset, label_dataset))
        # shuffle dataset
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])
        return self._build_dataset(dataset, mode='TRAIN')

    def build_eval_dataset(self, x_files, y_files):
        """Build dataset for evaluating.

        Args:
            x_files: A file path or a list of file paths, feature files in common.
            y_files: A file path or a list of file paths, label file in common.

        Returns:
            A tf.data.Dataset instance.
        """
        feature_dataset = self._build_dataset_from_files(x_files)
        label_dataset = self._build_dataset_from_files(y_files)
        dataset = tf.data.Dataset.zip((feature_dataset, label_dataset))
        # shuffle dataset
        dataset = dataset.shuffle(
            buffer_size=self.config['buffer_size'],
            seed=self.config['seed'],
            reshuffle_each_iteration=self.config['reshuffle_each_iteration'])
        return self._build_dataset(dataset, mode='EVAL')

    def build_predict_dataset(self, x_files):
        """Build dataset for predicting.

        Args:
            x_files: A file path or a list of file paths, feature file in common.

        Returns:
            A tf.data.Dataset instance.
        """
        dataset = self._build_dataset_from_files(x_files)
        return self._build_predict_dataset(dataset)
