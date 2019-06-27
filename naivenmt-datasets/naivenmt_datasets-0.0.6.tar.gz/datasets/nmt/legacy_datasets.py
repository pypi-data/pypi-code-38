import tensorflow as tf
from tensorflow.python.ops import lookup_ops

from deprecated import deprecated


@deprecated(reason="Use nmt_dataset instead.")
class LegacyDataset:
    """Build dataset for https://github.com/luozhouyang/naivenmt.
    Each batch of dataset has multi fields, rather than only features and labels."""

    def __init__(self,
                 src_train_files,
                 tgt_train_files,
                 src_eval_files,
                 tgt_eval_files,
                 predict_files,
                 src_vocab_file,
                 tgt_vocab_file,
                 src_vocab_size,
                 tgt_vocab_size,
                 config=None):
        """Init.

        Args:
            src_train_files: A list of src train files
            tgt_train_files: A list of tgt train file
            src_eval_files: A list of src eval files
            tgt_eval_files: A list of tgt eval files
            predict_files: A list of src prediction files
            src_vocab_file: A vocab file for src language
            tgt_vocab_file: A vocab file for tgt language
            src_vocab_size: A integer, vocab size for src language
            tgt_vocab_size: A integer, vocab size for tgt language
            config: A dict, keys are described in _build_default_config method
        """
        self.src_train_files = src_train_files
        self.src_eval_files = src_eval_files
        self.tgt_train_files = tgt_train_files
        self.tgt_eval_files = tgt_eval_files
        self.predict_files = predict_files

        self.src_vocab_file = src_vocab_file
        self.tgt_vocab_file = tgt_vocab_file
        self.src_vocab_size = src_vocab_size
        self.tgt_vocab_size = tgt_vocab_size

        default_config = self._build_default_config()
        if config:
            default_config.update(config)
        self.config = default_config

        self.src_str2id_table = lookup_ops.index_table_from_file(
            self.src_vocab_file,
            vocab_size=self.src_vocab_size,
            default_value=self.config['unk_id'])
        self.src_id2str_table = lookup_ops.index_to_string_table_from_file(
            self.src_vocab_file,
            vocab_size=self.src_vocab_size,
            default_value=self.config['unk'])
        self.tgt_str2id_table = lookup_ops.index_table_from_file(
            self.tgt_vocab_file,
            vocab_size=self.tgt_vocab_size,
            default_value=self.config['unk_id'])
        self.tgt_id2str_table = lookup_ops.index_to_string_table_from_file(
            self.tgt_vocab_file,
            vocab_size=self.tgt_vocab_size,
            default_value=self.config['unk'])

    def build_train_dataset(self):
        """Build dataset for training."""
        src_dataset = tf.data.Dataset.from_tensor_slices(self.src_train_files)
        src_dataset = src_dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        tgt_dataset = tf.data.Dataset.from_tensor_slices(self.tgt_train_files)
        tgt_dataset = tgt_dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        dataset = tf.data.Dataset.zip((src_dataset, tgt_dataset))
        return self._build_dataset(dataset)

    def build_eval_dataset(self, ):
        """Build dataset for evaluation."""
        src_dataset = tf.data.Dataset.from_tensor_slices(self.src_eval_files)
        src_dataset = src_dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        tgt_dataset = tf.data.Dataset.from_tensor_slices(self.tgt_eval_files)
        tgt_dataset = tgt_dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        dataset = tf.data.Dataset.zip((src_dataset, tgt_dataset))
        return self._build_dataset(dataset)

    def build_predict_dataset(self, ):
        """Build dataset for prediction."""
        config = self.config
        dataset = tf.data.Dataset.from_tensor_slices(self.predict_files)
        dataset = dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        # prepare dataset for prediction

        dataset = dataset.map(
            lambda src: tf.strings.split([src], sep=config['delimiter']).values,
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.filter(lambda src: tf.size(src) > 0)

        if config['src_max_len'] > 0:
            dataset = dataset.map(
                lambda src: (src[:config['src_max_len']]),
                num_parallel_calls=config['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda src: tf.cast(self.src_str2id_table.lookup(src), tf.int32),
            num_parallel_calls=config['num_parallel_calls']
        )
        dataset = dataset.map(
            lambda src: (src, tf.size(src)),
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.padded_batch(
            batch_size=config['predict_batch_size'],
            padded_shapes=(
                tf.TensorShape([None]),
                tf.TensorShape([])),
            padding_values=(
                tf.constant(tf.cast(config['eos_id'], tf.int32)),
                0)
        )

        return dataset

    def _build_default_config(self):
        config = {
            'skip_count': 0,
            'repeat': 0,
            'shuffle': True,
            'reshuffle_each_iteration': True,
            'buffer_size': 1024 * 32,
            'delimiter': ' ',
            'num_parallel_calls': 4,
            'src_max_len': 50,
            'tgt_max_len': 50,
            'unk': 'unk',
            'sos': '<s>',
            'eos': '</s>',
            'unk_id': 0,  # first row in vocab
            'sos_id': 1,  # second row in vocab
            'eos_id': 2,  # third row in vocab
            'batch_size': 32,
            'predict_batch_size': 32,
            'seed': None
        }
        return config

    def _build_dataset(self, dataset):
        config = self.config
        if config['skip_count'] > 0:
            dataset = dataset.skip(config['skip_count'])
        if config['repeat'] > 0:
            dataset = dataset.repeat(config['repeat'])
        if config['shuffle']:
            dataset = dataset.shuffle(
                buffer_size=config['buffer_size'],
                seed=config['seed'],
                reshuffle_each_iteration=config['reshuffle_each_iteration'])

        # split
        dataset = dataset.map(
            lambda src, tgt: (tf.strings.split([src], sep=config['delimiter']).values,
                              tf.strings.split([tgt], sep=config['delimiter']).values),
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        # filter empty lines
        dataset = dataset.filter(
            lambda src, tgt: tf.logical_and(tf.size(src) > 0, tf.size(tgt) > 0)
        )

        # truncating
        if config['src_max_len'] > 0:
            dataset = dataset.map(
                lambda src, tgt: (src[:config['src_max_len']], tgt),
                num_parallel_calls=config['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)
        if config['tgt_max_len'] > 0:
            dataset = dataset.map(
                lambda src, tgt: (src, tgt[:config['tgt_max_len']]),
                num_parallel_calls=config['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        # add sos and eos
        dataset = dataset.map(
            lambda src, tgt: (
                src,
                tf.concat(([config['sos']], tgt), 0),
                tf.concat((tgt, [config['eos']]), 0)),
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)
        # convert str to ids
        dataset = dataset.map(
            lambda src, tgt_in, tgt_out: (
                tf.cast(self.src_str2id_table.lookup(src), tf.int32),
                tf.cast(self.tgt_str2id_table.lookup(tgt_in), tf.int32),
                tf.cast(self.tgt_str2id_table.lookup(tgt_out), tf.int32)),
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        # add size info
        dataset = dataset.map(
            lambda src, tgt_in, tgt_out: (src, tgt_in, tgt_out, tf.size(src), tf.size(tgt_out)),
            num_parallel_calls=config['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.padded_batch(
            batch_size=config['batch_size'],
            padded_shapes=(
                tf.TensorShape([None]),
                tf.TensorShape([None]),
                tf.TensorShape([None]),
                tf.TensorShape([]),
                tf.TensorShape([])),
            padding_values=(
                tf.constant(tf.cast(config['eos_id'], tf.int32)),
                tf.constant(tf.cast(config['sos_id'], tf.int32)),
                tf.constant(tf.cast(config['eos_id'], tf.int32)),
                0,
                0)
        )

        return dataset
