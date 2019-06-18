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

from .metric import Metric


class LML(Metric):
    """

    """

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

        if test_set:
            gp = model.get_posterior(train_set)
            data_set = test_set
        else:
            gp = model
            data_set = train_set

        result = gp.likelihood_function.get_log_likelihood(
            data_set,
            grad_needed=grad_needed
        )

        if grad_needed:
            prior_lml, gradient = result
            prior_lml = -float(prior_lml)
            gradient = -np.array(gradient)
            return prior_lml, gradient

        prior_lml = result
        prior_lml = -float(prior_lml)
        return prior_lml
