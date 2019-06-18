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

from .validation import Validation

class Cross(Validation):
    """

    """
    def __init__(self, n_folds, stratified=False, shuffle=True):
        self.n_folds = n_folds
        self.stratified = stratified
        self.shuffle = shuffle

    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """
        return self.split_data(
            data_set,
            n_reps=1,
            stratified=self.stratified,
            shuffle=self.shuffle,
            folds_n=self.n_folds,
            fold_len=None
        )
