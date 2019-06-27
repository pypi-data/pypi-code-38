import tensorflow as tf
from tensorflow.python.ops import lookup_ops
from deprecated import deprecated

__all__ = ['SourceDataset', 'TargetDataset', 'SourceTargetDataset']


@deprecated(reason="Use nmt_dataset instead.")
class _BaseDataset:
    """Build dataset for source language or target language files."""

    def __init__(self,
                 train_files,
                 eval_files,
                 vocab_file,
                 predict_files=None,
                 params=None):
        """Init.

        Args:
            train_files: A list of files for training
            eval_files: A list of files for evaluation
            predict_files: A list of files for prediction. Only needed for source language
            vocab_file: The vocab file
            params: A python dict, params to process dataset
        """
        self.train_files = train_files
        self.eval_files = eval_files
        self.predict_files = predict_files
        self.vocab_file = vocab_file

        # init params
        default_params = self.default_config()
        if params:
            default_params.update(**params)
        self.params = default_params
        # init str2id lookup table
        self.str2id = lookup_ops.index_table_from_file(self.vocab_file, default_value=self.params['unk_id'])

    def _create_dataset_from_files(self, files):
        dataset = tf.data.Dataset.from_tensor_slices(files)
        dataset = dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        return dataset

    def build_train_dataset(self):
        dataset = self._create_dataset_from_files(self.train_files)
        dataset = self._build_dataset(dataset, mode='train')
        return dataset

    def build_eval_dataset(self):
        dataset = self._create_dataset_from_files(self.eval_files)
        dataset = self._build_dataset(dataset, mode='eval')
        return dataset

    def build_predict_dataset(self):
        # target dataset does not need create dataset for prediction
        if not self.predict_files:
            return None
        dataset = self._create_dataset_from_files(self.predict_files)
        dataset = dataset.map(
            lambda line: tf.strings.split([line], sep=self.params['delimiter']).values,
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        if self.params['tgt_max_len'] > 0:
            dataset = dataset.map(
                lambda line: line[:self.params['tgt_max_len']],
                num_parallel_calls=self.params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda line: self.str2id.lookup(line),
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)
        dataset = dataset.padded_batch(
            batch_size=self.params['predict_batch_size'],
            padded_shapes=(tf.TensorShape([None])),
            padding_values=(tf.constant(self.params['unk_id'], dtype=tf.int64)))
        return dataset

    def _build_dataset(self, dataset, mode='train'):
        raise NotImplementedError()

    def default_config(self):
        params = {
            'unk_id': 0,
            'unk': '<unk>',
            'delimiter': ' ',
            'train_batch_size': 32,
            'eval_batch_size': 32,
            'predict_batch_size': 32,
            'num_parallel_calls': 4,
            'src_max_len': -1,
            'tgt_max_len': -1,
            'buffer_size': 100000

        }
        return params


class SourceDataset(_BaseDataset):
    """Build dataset for source language."""

    def __init__(self,
                 src_train_files,
                 src_eval_files,
                 src_predict_files,
                 src_vocab_file,
                 params=None):
        """Init.

        Args:
            src_train_files: A list of training files for source language
            src_eval_files: A list of evaluation files for source language
            src_predict_files: A list of prediction files for source language
            src_vocab_file: The vocab file for source language
            params: A python dict, params to process dataset
        """
        super(SourceDataset, self).__init__(
            train_files=src_train_files,
            eval_files=src_eval_files,
            predict_files=src_predict_files,
            vocab_file=src_vocab_file,
            params=params)

    def _build_dataset(self, dataset, mode='train'):
        # DO NOT shuffle!!! source and target dataset are different object, shuffle will broke src-tgt pair!
        dataset = dataset.map(
            lambda line: tf.strings.split([line], sep=self.params['delimiter']).values,
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        if self.params['src_max_len'] > 0:
            dataset = dataset.map(
                lambda src: src[:self.params['src_max_len']],
                num_parallel_calls=self.params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda src: self.str2id.lookup(src),
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        batch_size = self.params['train_batch_size'] if mode == 'train' else self.params['eval_batch_size']
        print('batch size: %d' % batch_size)
        dataset = dataset.padded_batch(
            batch_size=batch_size,
            padded_shapes=(tf.TensorShape([None])),
            padding_values=(tf.constant(self.params['unk_id'], dtype=tf.int64))
        ).prefetch(tf.data.experimental.AUTOTUNE)

        return dataset


@deprecated(reason="Use nmt_dataset instead.")
class TargetDataset(_BaseDataset):
    """Build dataset for target language."""

    def __init__(self,
                 tgt_train_files,
                 tgt_eval_files,
                 tgt_vocab_file,
                 params=None):
        """Init.

        Args:
            tgt_vocab_file: A list of training files for target language
            tgt_eval_files: A list of evaluation files for target language
            tgt_vocab_file: The vocab file for target language
            params: A python dict, params to process dataset
        """
        super(TargetDataset, self).__init__(
            train_files=tgt_train_files,
            eval_files=tgt_eval_files,
            predict_files=None,
            vocab_file=tgt_vocab_file,
            params=params)

    def _build_dataset(self, dataset, mode='train'):
        # DO NOT shuffle!!! source and target dataset are different object, shuffle will broke src-tgt pair!
        dataset = dataset.map(
            lambda line: tf.strings.split([line], sep=self.params['delimiter']).values,
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        if self.params['tgt_max_len'] > 0:
            dataset = dataset.map(
                lambda src: src[:self.params['src_max_len']],
                num_parallel_calls=self.params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda src: self.str2id.lookup(src),
            num_parallel_calls=self.params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        batch_size = self.params['train_batch_size'] if mode == 'train' else self.params['eval_batch_size']
        print('batch size: %d' % batch_size)
        dataset = dataset.padded_batch(
            batch_size=batch_size,
            padded_shapes=(tf.TensorShape([None])),
            padding_values=(tf.constant(self.params['unk_id'], dtype=tf.int64))
        ).prefetch(tf.data.experimental.AUTOTUNE)

        return dataset


@deprecated(reason="Use nmt_dataset instead.")
class SourceTargetDataset:

    def __init__(self,
                 src_train_files,
                 src_eval_files,
                 src_predict_files,
                 src_vocab_file,
                 tgt_train_files,
                 tgt_eval_files,
                 tgt_vocab_file,
                 params=None):
        # init params
        default_params = self.default_config()
        if params:
            default_params.update(**params)
        self.params = default_params

        self.source_dataset = SourceDataset(
            src_train_files, src_eval_files, src_predict_files, src_vocab_file, self.params)
        self.target_dataset = TargetDataset(
            tgt_train_files, tgt_eval_files, tgt_vocab_file, self.params)

    def default_config(self):
        params = {
            'unk_id': 0,
            'unk': '<unk>',
            'delimiter': ' ',
            'train_batch_size': 32,
            'eval_batch_size': 32,
            'predict_batch_size': 32,
            'num_parallel_calls': 4,
            'src_max_len': -1,
            'tgt_max_len': -1,
            'buffer_size': 100000
        }
        return params

    def build_train_dataset(self):
        src_dataset = self.source_dataset.build_train_dataset()
        tgt_dataset = self.target_dataset.build_train_dataset()
        dataset = tf.data.Dataset.zip((src_dataset, tgt_dataset))
        dataset = dataset.shuffle(buffer_size=self.params['buffer_size'])
        return dataset

    def build_eval_dataset(self):
        src_dataset = self.source_dataset.build_eval_dataset()
        tgt_dataset = self.target_dataset.build_eval_dataset()
        dataset = tf.data.Dataset.zip((src_dataset, tgt_dataset))
        dataset = dataset.shuffle(buffer_size=self.params['buffer_size'])
        return dataset

    def build_predict_dataset(self):
        src_dataset = self.source_dataset.build_predict_dataset()
        return src_dataset
