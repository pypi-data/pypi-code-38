# -*- coding: utf-8 -*-
import six
import abc

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


@six.add_metaclass(abc.ABCMeta)
class _Iterator(object):
    """Base class for image data iterators.

    Every `Iterator` must implement the `_get_batches_of_transformed_samples`
    method.

    # Arguments
        n: Integer, total number of samples in the dataset to loop over.
        batch_size: Integer, size of a batch.
    """

    def __init__(self, data_generator):
        self._data_generator = data_generator
        self._batch_index = 0

    def __len__(self):
        return len(self._data_generator)

    def __iter__(self):
        # Needed if we want to do something like:
        # for x, y in data_gen.flow(...):
        return self

    def __next__(self):
        return self._next()

    @abc.abstractmethod
    def _next(self):
        """
        The actual __next__ implementation of the concrete iterator
        """

    def _has_reached_iterator_boundary(self):
        return self._batch_index >= len(self._data_generator)

    def _get_current_item(self):
        return self._data_generator[self._batch_index]

    def _increment_index(self):
        self._batch_index += 1

    next = __next__


class _InfiniteIterator(_Iterator):

    def reset(self):
        self._batch_index = 0

    def _next(self):
        results = self._get_current_item()

        self._increment_index()

        if self._has_reached_iterator_boundary():
            self.reset()

        return results


class _FiniteIterator(_Iterator):

    def _next(self):
        if self._has_reached_iterator_boundary():
            raise StopIteration

        results = self._get_current_item()

        self._increment_index()

        return results
