# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np


class Metric(object):
    """

    """

    def fold_measure(self, model, folds, grad_needed=False):
        """

        :param model:
        :type model:
        :param folds:
        :type folds:
        :param grad_needed:
        :type grad_needed:
        :return:
        :rtype:
        """
        results = [
            self.measure(
                model,
                train_set=train_set,
                test_set=test_set,
                grad_needed=grad_needed)
            for train_set, test_set in folds
        ]

        if not grad_needed:
            return np.mean(results)

        value, gradient = zip(*results)

        # TODO check this

        return np.mean(value), np.mean(np.vstack(gradient), axis=0)

    @staticmethod
    def measure(model, train_set, test_set=None, grad_needed=False):
        """

        :param model:
        :type model:
        :param train_set:
        :type train_set:
        :param test_set:
        :type test_set:
        :param grad_needed:
        :type grad_needed:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
