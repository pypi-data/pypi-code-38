import functools

import tensorflow as tf


def index_table_from_file(vocabulary_file=None):
    index_table = {}
    index_counter = 0
    with open(vocabulary_file) as fd:
        for line in fd:
            key = line.strip()
            index_table[key] = index_counter
            index_counter += 1

    class Lookuper(object):
        def __init__(self, index_table):
            self.index_table = index_table

        def lookup(self, string):
            return self.index_table.get(string)

    return Lookuper(index_table)


def to_fixed_len(words, fixed_len, defaults_words):
    if len(words) < fixed_len:
        for _ in range(fixed_len - len(words)):
            words.append(defaults_words)
    else:
        words = words[:fixed_len]

    return words


def generator_func(data_generator_func, config):
    for sentence in data_generator_func():
        words, label = parse_fn(sentence)
        if config.get('max_seq_length'):
            words = to_fixed_len(words, config.get('max_seq_length'), config.get('default_value'))

        yield words, label


def parse_fn(offset_data):
    label = offset_data.label
    words = [i for i in offset_data.text]

    return words, label


def parse_to_dataset(data_generator_func, config=None,
                     shuffle_and_repeat=False):
    config = config if config is not None else {}
    shapes = [None], ()
    types = tf.string, tf.string
    defaults = '<pad>', '<pad_label>'

    dataset = tf.data.Dataset.from_generator(
        functools.partial(generator_func, data_generator_func, config),
        output_shapes=shapes, output_types=types)

    if shuffle_and_repeat:
        # print(">>> {}".format(config))
        dataset = dataset.shuffle(config['shuffle_pool_size']).repeat(
            config['epochs'])

    # char_encoder = tfds.features.text.SubwordTextEncoder.load_from_file(read_assets()['vocab_filename'])
    # tag_encoder = tfds.features.text.SubwordTextEncoder.load_from_file(read_assets()['tag_filename'])
    # dataset = dataset.map(lambda x: (char_encoder.encode(x[0][0]), tag_encoder.encode(x[0][1]), x[1]))

    # words_index_table = index_table_from_file(read_assets()['vocab_filename'])
    # tags_index_table = index_table_from_file(read_assets()['tag_filename'])
    # dataset = dataset.map(lambda x, y: ((words_index_table.lookup(x[0]), x[1]), tags_index_table.lookup(y)))

    if False:
        dataset = (dataset
                   .padded_batch(config['batch_size'], shapes, defaults)
                   .prefetch(1))
    else:
        dataset = (dataset
                   .batch(config['batch_size'],
                          drop_remainder=True)  # drop_remainder needed by TPU
                   .prefetch(1))

    return dataset


def dataset_to_feature_column(dataset):
    words, label = dataset.make_one_shot_iterator().get_next()

    # word_index_lookuper = tf.contrib.lookup.index_table_from_file(
    #     read_assets()['vocab_filename'],
    #     num_oov_buckets=1
    # )
    # words = word_index_lookuper.lookup(words)
    #
    # tag_index_lookuper = tf.contrib.lookup.index_table_from_file(
    #     read_assets()['tag_filename'],
    #     num_oov_buckets=1
    # )
    # label = tag_index_lookuper.lookup(label)

    return {'words': words}, label


def build_input_func(data_generator_func, config=None):
    def input_func():
        train_dataset = parse_to_dataset(data_generator_func, config,
                                         shuffle_and_repeat=True)
        data_iterator = dataset_to_feature_column(train_dataset)

        return data_iterator

    return input_func


def build_gold_generator_func(offset_dataset):
    return functools.partial(generator_func, offset_dataset)

