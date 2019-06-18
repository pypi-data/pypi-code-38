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


class Validation(object):
    """

    """
    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    @staticmethod
    def split_data(data_set, n_reps, stratified, shuffle, folds_n, fold_len):
        """

        :param data_set:
        :type data_set:
        :param n_reps:
        :type n_reps:
        :param stratified:
        :type stratified:
        :param shuffle:
        :type shuffle:
        :param folds_n:
        :type folds_n:
        :param fold_len:
        :type fold_len:
        :return:
        :rtype:
        """

        folds = []

        if stratified:
            groups = [
                np.argwhere(data_set['Y'] == y)[:, 0]
                for y in np.unique(data_set['Y'])
            ]
        else:
            groups = [np.arange(data_set['X'].shape[0])]

        for _ in range(n_reps):
            if shuffle:
                groups = [
                    group[np.random.permutation(len(group))]
                    for group in groups
                ]
            for fold_i in range(folds_n):
                train_selection = np.array([], dtype=np.int64)
                test_selection = np.array([], dtype=np.int64)
                for group in groups:
                    n = len(group)
                    if fold_len is not None:
                        rel_fold_len = \
                            int(np.ceil(float(n) * fold_len))
                    else:
                        rel_fold_len = \
                            int(np.ceil(float(n) / folds_n))
                    cut1 = max(n - (rel_fold_len * (fold_i + 1)), 0)
                    cut2 = n - (rel_fold_len * fold_i)
                    train_slice1 = slice(None, cut1, None)
                    test_slice = slice(cut1, cut2, None)
                    train_slice2 = slice(cut2, None, None)
                    train_selection = np.concatenate((
                        train_selection,
                        group[train_slice1],
                        group[train_slice2]
                    ))
                    test_selection = np.concatenate((
                        test_selection,
                        group[test_slice]
                    ))
                train_set = {
                    name: element[train_selection, :]
                    for name, element in data_set.items()
                }
                test_set = None
                if len(test_selection) > 0:
                    test_set = {
                        name: element[test_selection, :]
                        for name, element in data_set.items()
                    }
                folds.append((train_set, test_set))

        return folds
