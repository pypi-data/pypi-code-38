import tensorflow as tf
from deprecated import deprecated
from tensorflow.python.ops import lookup_ops

__all__ = ["QueryDocSameFileDataset", "QueryDocSeparateFilesDataset"]


def label_normalize_fn(x):
    """Normalize labels.
        For binary classification problem, one may use `0` or `1 0` to identify negative example,
    use `1` or `0 1` to identify positive examples.

    Args:
        x: A tensor, label

    Returns:
        A tensor, 0 or 1
    """
    res = tf.cond(
        tf.logical_or(tf.equal(x, '1'), tf.equal(x, '0 1')),
        lambda: tf.constant(1, dtype=tf.int32),
        lambda: tf.constant(0, dtype=tf.int32)
    )
    return res


@tf.function
def label_normalize_fn_v2(x):
    if x == '1' or x == '0 1':
        return 1
    return 0


@deprecated(reason="Use dssm_dataset instead.")
class _BaseQueryDocDataset:

    def build_train_dataset(self, train_files):
        raise NotImplementedError()

    def build_eval_dataset(self, eval_file):
        raise NotImplementedError()

    def build_predict_dataset(self, predict_files):
        raise NotImplementedError()

    def default_config(self):
        params = {
            'unk_id': 0,
            'unk': '<unk>',
            'delimiter': '@',  # split line to query and doc
            'separator': ' ',  # split query or doc to words
            'num_parallel_calls': 4,
            'query_max_len': None,
            'doc_max_len': None,
            'train_batch_size': 32,
            'eval_batch_size': 32,
            'predict_batch_size': 32,
            'skip_count': 0,
            'shuffle': True,
            'buffer_size': 1000000,
            'reshuffle_each_iteration': False,
            'seed': 1000000
        }
        return params

    def _build_dataset(self, dataset, str2id_table, params, mode='train'):
        dataset = dataset.map(
            lambda query, doc, label: (
                tf.strings.split([query], sep=params['separator']).values,
                tf.strings.split([doc], sep=params['separator']).values,
                label),
            num_parallel_calls=params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        if params['query_max_len']:
            dataset = dataset.map(
                lambda query, doc, label: (query[:params['query_max_len']], doc, label),
                num_parallel_calls=params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)
        if params['doc_max_len']:
            dataset = dataset.map(
                lambda query, doc, label: (query, doc[:params['doc_max_len']], label),
                num_parallel_calls=params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda query, doc, label: (
                str2id_table.lookup(query),
                str2id_table.lookup(doc),
                label),
            num_parallel_calls=params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        batch_size = params['train_batch_size'] if mode == 'train' else params['eval_batch_size']
        dataset = dataset.padded_batch(
            batch_size=batch_size,
            padded_shapes=(tf.TensorShape([None]), tf.TensorShape([None]), tf.TensorShape([])),
            padding_values=(
                tf.constant(tf.cast(params['unk_id'], dtype=tf.int64)),
                tf.constant(tf.cast(params['unk_id'], dtype=tf.int64)),
                0)
        )

        dataset = dataset.map(lambda query, doc, label: ((query, doc), label)).prefetch(tf.data.experimental.AUTOTUNE)
        return dataset

    def _build_predict_dataset(self, dataset, str2id_table, params):
        dataset = dataset.map(
            lambda query, doc: (
                tf.strings.split([query], sep=params['separator']).values,
                tf.strings.split([doc], sep=params['separator']).values),
            num_parallel_calls=params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        if params['query_max_len']:
            dataset = dataset.map(
                lambda query, doc: (query[:params['query_max_len']], doc),
                num_parallel_calls=params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        if params['doc_max_len']:
            dataset = dataset.map(
                lambda query, doc: (query, doc[:params['doc_max_len']]),
                num_parallel_calls=params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.map(
            lambda query, doc: (str2id_table.lookup(query), str2id_table.lookup(doc)),
            num_parallel_calls=params['num_parallel_calls']
        ).prefetch(tf.data.experimental.AUTOTUNE)

        dataset = dataset.padded_batch(
            batch_size=params['predict_batch_size'],
            padded_shapes=(tf.TensorShape([None]), tf.TensorShape([None])),
            padding_values=(
                tf.constant(params['unk_id'], dtype=tf.int64), tf.constant(params['unk_id'], dtype=tf.int64))
        ).prefetch(tf.data.experimental.AUTOTUNE)
        dataset = dataset.map(lambda query, doc: ([query, doc]))
        return dataset

    def _skip_dataset(self, dataset, params):
        if params['skip_count'] > 0:
            dataset = dataset.flat_map(lambda x: tf.data.TextLineDataset(x).skip(params['skip_count']))
        else:
            dataset = dataset.flat_map(lambda x: tf.data.TextLineDataset(x))
        return dataset

    def _shuffle_dataset(self, dataset, params):
        if params['shuffle']:
            dataset = dataset.shuffle(
                buffer_size=params['buffer_size'],
                seed=params['seed'],
                reshuffle_each_iteration=params['reshuffle_each_iteration'])
        return dataset


@deprecated(reason="Use dssm_dataset instead.")
class QueryDocSameFileDataset(_BaseQueryDocDataset):
    """Build dataset for DSSM network, produce ([query, doc], label) data.
    Query, doc and label are saved in the same files, separated by a special separator. e.g '@'.
    """

    def __init__(self,
                 vocab_file,
                 params=None):
        """Init.

        Args:
            vocab_file: The vocab file, `<unk>` should put in the first line
            params: A python dict(Optional), configurations
        """
        self.vocab_file = vocab_file

        default_config = self.default_config()
        if params:
            default_config.update(**params)
        self.params = default_config

        self.str2id = lookup_ops.index_table_from_file(self.vocab_file, default_value=self.params['unk_id'])

    def _create_dataset_from_files(self, files):
        dataset = tf.data.Dataset.from_tensor_slices(files)
        dataset = self._skip_dataset(dataset, self.params)
        dataset = self._shuffle_dataset(dataset, self.params)
        dataset = dataset.filter(
            lambda x: tf.equal(tf.size(tf.strings.split([x], sep=self.params['delimiter']).values), 3))
        dataset = dataset.map(
            lambda x: (tf.strings.split([x], sep=self.params['delimiter']).values[0],
                       tf.strings.split([x], sep=self.params['delimiter']).values[1],
                       tf.strings.split([x], sep=self.params['delimiter']).values[2]),
            num_parallel_calls=self.params['num_parallel_calls'])

        dataset = dataset.map(
            lambda query, doc, label: (query, doc, label_normalize_fn(label)),
            num_parallel_calls=self.params['num_parallel_calls'])

        dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
        return dataset

    def build_train_dataset(self, train_files):
        """Build dataset for training.

        Args:
            train_files: A list of training files, each line contains query, doc and label.

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(train_files)
        # process dataset
        dataset = self._build_dataset(dataset, self.str2id, self.params, mode='train')
        return dataset

    def build_eval_dataset(self, eval_files):
        """Build dataset for evaluation.

        Args:
            eval_files: A list of evaluation files, each line contains query, doc and label.

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(eval_files)
        # process dataset
        dataset = self._build_dataset(dataset, self.str2id, self.params, mode='eval')
        return dataset

    def build_predict_dataset(self, predict_files):
        """Build dataset for prediction.

        Args:
            predict_files: A list of prediction files, each line contains query, doc and label, label is not used.

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(predict_files)
        dataset = dataset.map(
            lambda query, doc, label: (query, doc),
            num_parallel_calls=self.params['num_parallel_calls']
        )
        # process dataset
        dataset = self._build_predict_dataset(dataset, self.str2id, self.params)
        return dataset


@deprecated(reason="Use dssm_dataset instead.")
class QueryDocSeparateFilesDataset(_BaseQueryDocDataset):
    """Build dataset for DSSM network, produce ([query, doc], label) data.
    Query, doc and label files are saved in difference files.
    """

    def __init__(self,
                 vocab_file,
                 params=None):
        """Init.

        Args:
            vocab_file: The vocab file, `<unk>` should put in the first line
            params: A python dict(Optional), configurations
        """
        self.vocab_file = vocab_file

        default_params = self.default_config()
        if params:
            default_params.update(**params)
        self.params = default_params

        self.str2id = lookup_ops.index_table_from_file(self.vocab_file, default_value=self.params['unk_id'])

    def _create_dataset_from_files(self, files):
        query, doc, label = files
        query_dataset = tf.data.Dataset.from_tensor_slices(query)
        query_dataset = self._skip_dataset(query_dataset, self.params)

        doc_dataset = tf.data.Dataset.from_tensor_slices(doc)
        doc_dataset = self._skip_dataset(doc_dataset, self.params)

        if label:
            label_dataset = tf.data.Dataset.from_tensor_slices(label)
            label_dataset = self._skip_dataset(label_dataset, self.params)
            label_dataset = label_dataset.map(
                lambda label: label_normalize_fn(label),
                num_parallel_calls=self.params['num_parallel_calls']
            ).prefetch(tf.data.experimental.AUTOTUNE)

            dataset = tf.data.Dataset.zip((query_dataset, doc_dataset, label_dataset))
        else:
            dataset = tf.data.Dataset.zip((query_dataset, doc_dataset))

        # shuffle
        dataset = self._shuffle_dataset(dataset, self.params)
        return dataset

    def build_train_dataset(self, train_files):
        """Build dataset for training.

        Args:
            train_files: A tuple(query_files, doc_files, label_files)

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(train_files)
        # process dataset
        dataset = self._build_dataset(dataset, self.str2id, self.params, mode='train')
        return dataset

    def build_eval_dataset(self, eval_files):
        """Build dataset for evaluations.

        Args:
            eval_files: A tuple(query_files, doc_files, label_files)

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(eval_files)
        # process dataset
        dataset = self._build_dataset(dataset, self.str2id, self.params, mode='eval')
        return dataset

    def build_predict_dataset(self, predict_files):
        """Build dataset for prediction.

        Args:
            predict_files: A tuple(query_files, doc_files, label_files or None)

        Returns:
            A tf.data.Dataset object.
        """
        dataset = self._create_dataset_from_files(predict_files)
        # process dataset
        dataset = self._build_predict_dataset(dataset, self.str2id, self.params)
        return dataset
