#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Function to create random integer

"""
import random

__all__ = ["reject_random", "filter_random", "FilterRandom"]


def reject_random(min_value=-10, max_value=10, rejected=[0, 1], accept_callbacks=[]):
    """ Generate a random integer with the rejection method

        :param name: name of the Integer
        :param min_value: minimum value
        :param max_value: maximum value
        :param rejected: rejected values
        :param accept_callbacks: list of function for value rejection

        :example:
        >>> a = reject_random()
        >>> a not in [0, 1]
        True
        >>> a >= -10
        True
        >>> a <= 10
        True
        >>> a = reject_random(min_value=3, max_value=11, rejected=[5, 7])
        >>> a not in [5, 7]
        True
        >>> a >= 3
        True
        >>> a <= 11
        True
        >>> a = reject_random(accept_callbacks=[lambda x: x%2])
        >>> a%2
        1
        >>> random.seed(0)
        >>> reject_random()
        2
        >>> random.seed(1)
        >>> reject_random()
        -6

    """
    conditions = [lambda x: x not in rejected] + accept_callbacks

    candidate = random.randint(min_value, max_value)
    while not all(c(candidate) for c in conditions):
        candidate = random.randint(min_value, max_value)

    return candidate


def filter_random(min_value=-10, max_value=10, rejected=[0, 1], accept_callbacks=[]):
    """ Generate a random integer by filtering then choosing a candidate

        :param name: name of the Integer
        :param min_value: minimum value
        :param max_value: maximum value
        :param rejected: rejected values
        :param accept_callbacks: list of function for value rejection

        :example:
        >>> a = filter_random()
        >>> a not in [0, 1]
        True
        >>> a >= -10
        True
        >>> a <= 10
        True
        >>> a = filter_random(min_value=3, max_value=11, rejected=[5, 7])
        >>> a not in [5, 7]
        True
        >>> a >= 3
        True
        >>> a <= 11
        True
        >>> a = filter_random(accept_callbacks=[lambda x: x%2])
        >>> a%2
        1
        >>> random.seed(0)
        >>> filter_random()
        -7
        >>> random.seed(1)
        >>> filter_random()
        6
    """
    candidates = set(range(min_value, max_value + 1))
    candidates = {c for c in candidates if c not in rejected}

    candidates = [
        candidate
        for candidate in candidates
        if all(c(candidate) for c in accept_callbacks)
    ]

    if len(candidates) == 0:
        raise OverflowError(
            "There is no candidates for this range and those conditions"
        )
    return random.choice(candidates)


class FilterRandom(object):

    """ Integer random generator which filter then choose candidate
    """

    # TODO: Faire un cache pour éviter de reconstruire les listes à chaque fois |ven. déc. 21 19:07:42 CET 2018

    def __init__(
        self, rejected=[0, 1], accept_callbacks=[], min_value=-10, max_value=10
    ):
        self.conditions = (lambda x: x not in rejected,) + tuple(accept_callbacks)

        self._min = min_value
        self._max = max_value

        candidates = set(range(self._min, self._max + 1))

        self._candidates = {
            candidate
            for candidate in candidates
            if all(c(candidate) for c in self.conditions)
        }

    def add_candidates(self, low, high):
        """ Add candidates between low and high to _candidates """
        if low < self._min:
            self._min = low
            useless_low = False
        else:
            useless_low = True
        if high > self._max:
            self._max = high
            useless_high = False
        else:
            useless_high = True

        if not (useless_low and useless_high):
            candidates = set(range(low, high + 1))

            self._candidates = self._candidates.union(
                {
                    candidate
                    for candidate in candidates
                    if all(c(candidate) for c in self.conditions)
                }
            )

    def candidates(self, min_value=-10, max_value=10):
        """ Return candidates between min_value and max_value """
        return [c for c in self._candidates if (c > min_value and c < max_value)]

    def __call__(self, min_value=-10, max_value=10):
        """ Randomly choose on candidate """
        self.add_candidates(min_value, max_value)
        return random.choice(self.candidates(min_value, max_value))


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
