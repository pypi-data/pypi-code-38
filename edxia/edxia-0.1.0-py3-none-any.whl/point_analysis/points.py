# Copyright (c) 2019 Fabien Georget <fabien.georget@epfl.ch>, EPFL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
import pandas as pd
from py_expression_eval import Parser
from ..utils.chemistry import molar_masses
from ..core.experiment import PartOfExperiment

def get_data(df, anexpr):
    """Perform simple mathematical expressions on the series of a dataframe

    :param df: Pandas dataframe
    :param anexpr: simple mathematical expressions where variables are the name of the columns
    :returns: new data series formed from the mathematical expression given
    """
    parser = Parser()
    toeval = parser.parse(anexpr)
    try:
        var_dict = dict([(ci, df[ci]) for ci in toeval.variables()])
    except KeyError:
        var_dict = dict([(ci, df.get(ci, 0.0)) for ci in toeval.variables()])
    return toeval.evaluate(var_dict)


class EDSPoints(PartOfExperiment):
    """A set of points from EDSanalysis"""
    def __init__(self, data_df, parent):
        super().__init__(parent)
        self._data = data_df


    @property
    def df(self):
        """Returns the underlying pandas dataframe."""
        return self._data

    def __getitem__(self, key):
        """Returns the points for the given key.

        :param key: a column, or a simple mathematical expression made of the columns
        """
        return get_data(self._data, key)

    def to_atomic(self, copy=True):
        """Transforms points to atomic

        :param copy: if True, return a new instance with the atomic values
        """
        if copy:
            dfc = self.df.copy()
        else:
            dfc = self.df
        totc = np.zeros((dfc.shape[0],))
        for c, val in molar_masses.items():
            if not c in dfc:
                continue
            dfc.loc[:,c] /= val
            totc += dfc[c]
        for c in molar_masses.keys():
            if not c in dfc:
                continue
            dfc.loc[:,c] /= totc
        if copy:
            return EDSPoints(dfc)
        else:
            return self

    def add_column(self, name, expr):
        """Add a column to the dataset

        :param name: name of the new column
        :param expr: expression used to compute the values
        """
        self._data[name] = get_data(self._data, expr)


def points_from_segmentation(map_stack, labels, mask_img=None, include_rc=True, include_yx=True):
    """Extract data from a map stack using a set of labels.

    :param map_stack: a stack of EDS maps
    :param labels: labels issued from a segmentation
    "param mask_img: do not consider labels where mask_img is black
    :param include_rc: If True, include row,column as data series
    :returns: an EDSPoints instance

    """
    centroids = labels.get_center_labels()
    dfdict = {}
    if mask_img is not None:
        if len(mask_img.shape) == 3:
            mask = np.array([(mask_img[centroids[ind,0],centroids[ind,1],:].sum()==0) for ind in range(centroids.shape[0])])
        else:
            mask = np.array([(mask_img[centroids[ind,0],centroids[ind,1]].sum()==0) for ind in range(centroids.shape[0])])
    else:
        mask = np.full((centroids.shape[0],), False)
    if include_rc:
        dfdict["r"] = centroids[~mask,0]
        dfdict["c"] = centroids[~mask,1]
    if include_yx:
        dfdict["y"] = map_stack.shape[0]-centroids[~mask,0]
        dfdict["x"] = centroids[~mask,1]
    for ind,c in enumerate(map_stack.components):
        dfdict[c] = map_stack[centroids[~mask,0], centroids[~mask,1],ind]
    return EDSPoints(pd.DataFrame(data=dfdict), map_stack.parent)
