"""
    Input pipeline
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools

import tensorflow as tf

from tflibs.utils import compose_funcs
from tflibs.ops import randomly_pick_op


def build_input_fn(dataset_fn,
                   batch_size,
                   map_fn=None,
                   global_step=None,
                   num_elements=None,
                   consider_num_elements=True,
                   shuffle_and_repeat=True,
                   num_parallel_batches=1,
                   shuffle_buffer_size=50,
                   prefetch_buffer_size=20):
    def input_fn():
        dataset = dataset_fn()  # type: tf.data.Dataset

        if consider_num_elements:
            num_elem = num_elements or _count_dataset(dataset)
            tf.logging.info('Number of elements in dataset {}: {}'.format(dataset, num_elem))

            if global_step:
                dataset = dataset.skip(((global_step - 1) * batch_size) % num_elem)

        if shuffle_and_repeat:
            dataset = dataset.apply(tf.data.experimental.shuffle_and_repeat(batch_size * shuffle_buffer_size))

        if map_fn is not None:
            dataset = dataset.apply(tf.data.experimental.map_and_batch(map_fn, batch_size, drop_remainder=True,
                                                                       num_parallel_batches=num_parallel_batches))
        else:
            dataset = dataset.batch(batch_size, drop_remainder=True)

        dataset = dataset.prefetch(buffer_size=prefetch_buffer_size)
        return dataset

    return input_fn


def _count_dataset(dataset: tf.data.Dataset):
    iterator = dataset.make_one_shot_iterator()
    elem = iterator.get_next()

    with tf.Session() as sess:
        counts = 0
        while True:
            try:
                sess.run(elem)
                counts += 1
            except tf.errors.OutOfRangeError:
                break

    return counts


def augment_data_op(augment_fns: list):
    with tf.name_scope('augment_data'):
        def binary_counter(length):
            return itertools.product(range(2), repeat=length)

        def binary_selection(col):
            return [itertools.compress(col, list(bin)) for bin in binary_counter(len(col))]

        augs = [compose_funcs(*selected) for selected in binary_selection(augment_fns)]

        aug = randomly_pick_op(augs)

        return aug
