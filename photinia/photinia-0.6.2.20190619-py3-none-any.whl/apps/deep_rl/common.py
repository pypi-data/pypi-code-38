#!/usr/bin/env python3

"""
@author: xi
@since: 2018-06-20
"""

import random

import numpy as np
import tensorflow as tf

import photinia as ph


class ReplayMemory(object):

    def __init__(self, buffer_size):
        """Replay memory.

        Args:
            buffer_size (int): Max buffer size.

        """
        self._buffer_size = buffer_size
        self._buffer = list()
        self._pointer = 0

    def full(self):
        return len(self._buffer) >= self._buffer_size

    def put(self, s, a, r, s_, done):
        """Put a transition tuple to the replay memory.

        Args:
            s (numpy.ndarray): State s_t.
            a ((numpy.ndarray)): Action a_t.
            r (float): Reward r_{t + 1}.
            s_ (numpy.ndarray): Transition state s_{t + 1}.
            done (bool): Is terminal?

        """
        row = (s, a, r, s_, done)
        if len(self._buffer) < self._buffer_size:
            self._buffer.append(row)
        else:
            self._buffer[self._pointer] = row
            self._pointer = (self._pointer + 1) % self._buffer_size

    def get(self, batch_size):
        """Get a random batch of transitions from the memory.

        Args:
            batch_size (int): Batch size.

        Returns:
            list[tuple]: List of transition tuples.

        """
        if batch_size <= len(self._buffer):
            rows = random.sample(list(self._buffer), batch_size)
        else:
            rows = self._buffer
        columns = (list(), list(), list(), list(), list())
        for row in rows:
            for i in range(5):
                columns[i].append(row[i])
        return columns


class NormalNoise(object):

    def __init__(self, init_stddev, low_bound=-1, high_bound=1):
        self._stddev = init_stddev
        self._low_bound = low_bound
        self._high_bound = high_bound

    def add_noise(self, center):
        return np.clip(
            np.random.normal(center, self._stddev),
            self._low_bound,
            self._high_bound
        )

    def discount(self, factor=0.999):
        self._stddev *= factor
