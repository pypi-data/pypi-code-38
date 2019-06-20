# -*- coding: utf-8 -*-
import numpy as np


class _IteratorShuffle(object):
    def __init__(self, shuffle, count, seed):
        self.__random_seed = np.random.RandomState(seed)
        self.__batch_index_order = range(count)
        self.__shuffle = shuffle

    def reset(self):
        if self.__shuffle:
            self.__batch_index_order = self.__random_seed.permutation(self.__batch_index_order)

    def __getitem__(self, idx):
        return self.__batch_index_order[idx]


class _Iterator(object):
    """Base class for image data iterators.

    Every `Iterator` must implement the `_get_batches_of_transformed_samples`
    method.

    # Arguments
        n: Integer, total number of samples in the dataset to loop over.
        batch_size: Integer, size of a batch.
    """

    def __init__(self, data_generator):
        self.__data_generator = data_generator
        self.__batch_index = 0

    def reset(self):
        self.__batch_index = 0

    def __len__(self):
        return len(self.__data_generator)

    def __iter__(self):
        # Needed if we want to do something like:
        # for x, y in data_gen.flow(...):
        return self

    def __next__(self):
        results = self.__data_generator[self.__batch_index]

        self.__batch_index += 1

        if self.__batch_index >= len(self.__data_generator):
            self.reset()

        return results

    next = __next__
