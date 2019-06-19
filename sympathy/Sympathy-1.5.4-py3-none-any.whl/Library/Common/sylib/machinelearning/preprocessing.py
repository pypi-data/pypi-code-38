# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sylib.machinelearning.descriptors import Descriptor

import numpy as np

import sklearn

class StandardScalerDescriptor(Descriptor):
    pass


class RobustScalerDescriptor(Descriptor):
    pass

class MaxAbsScalerDescriptor(Descriptor):
    pass

class LabelBinarizerDescriptor(Descriptor):

    def post_fit(self, skl):
        """Assign the model classes as Y parameter names"""
        self.set_y_names(skl.classes_)


class OneHotEncoderDescriptor(Descriptor):

    def post_fit(self, skl):
        """Compute labels for each output from the OneHotEncoder"""

        indices = skl.feature_indices_
        y_names = []
        if self.x_names is None: return
        feature_idx = 0
        for feature, (start, stop) in enumerate(zip(indices[:-1], indices[1:])):
            feature_name = self.x_names[feature]
            for i in range(stop-start):
                if feature_idx in skl.active_features_:
                    y_names.append("{0}_{1}".format(feature_name,i))
                feature_idx = feature_idx + 1
        self.set_y_names(y_names)
        # TODO - logic to compute the names for columns that are
        # not "categorial" and just passed through the SKL node


class PolynomialFeaturesDescriptor(Descriptor):

    def post_fit(self, skl):
        y_names = []
        x_names = self.x_names or ["X{0}".format(i) for i in range(skl.n_input_features_)]
        for row in range(skl.n_output_features_):
            name=""
            for col in range(skl.n_input_features_):
                power = skl.powers_[row,col]
                if power > 0:
                    if name != "": name += " * "
                    name += x_names[col]
                if power > 1:
                    name += "^{0}".format(power)
            if name == "": name = "bias"
            y_names.append(name)
        self.set_y_names(y_names)

class  CategoryEncoderDescriptor(Descriptor):

    def __init__(self):
        super(CategoryEncoderDescriptor, self).__init__()

class  CategoryEncoder(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):

    def __init__(self, max_categories=None):
        super(CategoryEncoder, self).__init__()
        self.max_categories = max_categories

    def fit(self, X):
        self.categories_ = []
        self.inv_categories_ = []
        for col in range(X.shape[1]):
            all_values = np.array(list(set(X[:,col])))
            if self.max_categories is not None:
                count = np.array([np.sum(X[:,col] == val) for val in all_values], dtype=int)
                s = np.argsort(-count)
                all_values = all_values[s]
                all_values = all_values[:self.max_categories]
            all_values.sort()
            cats = {val: pos+1 for pos,val in enumerate(all_values)}
            self.categories_.append(cats)
            inv_cats = {pos+1: val for pos,val in enumerate(all_values)}
            self.inv_categories_.append(inv_cats)

    def transform(self, X):
        result = np.full(X.shape, 0, dtype=int)
        for col in range(X.shape[1]):
            dct = self.categories_[col]
            for key, val in dct.items():
                result[:, col][X[:, col] == key] = val
        return result

    def inverse_transform(self, X):
        result = np.zeros(X.shape, dtype='O')
        maxlen = 1
        for col in range(X.shape[1]):
            dct = self.inv_categories_[col]
            for key, val in dct.items():
                maxlen = max(maxlen, len(str(val)))
                result[:, col][X[:, col] == key] = str(val)
        try:
            result = result.astype(int)
        except ValueError:
            try:
                result = result.astype(float)
            except ValueError:
                result = result.astype('S{}'.format(maxlen))
        return np.array(result)

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_params(self, deep=False):
        return {}

    def set_params(self, **params):
        pass
