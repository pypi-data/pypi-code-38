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


class RandFold(Validation):
    """

    """
    def __init__(self, n_folds, fold_len, stratified=False):
        self.n_folds = n_folds
        self.fold_len = fold_len
        self.stratified = stratified

    def get_folds(self, data_set):
        """

        :param data_set:
        :type data_set:
        :return:
        :rtype:
        """
        return self.split_data(
            data_set,
            n_reps=self.n_folds,
            stratified=self.stratified,
            shuffle=True,
            folds_n=1,
            fold_len=self.fold_len
        )
