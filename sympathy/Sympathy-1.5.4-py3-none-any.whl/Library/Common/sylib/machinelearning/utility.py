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
import six
import base64
import pickle
import numbers
import numpy as np
import scipy.sparse
import distutils.spawn

from sympathy.platform import version_support as vs
from sympathy.api import table
from sympathy.api.nodeconfig import settings
from sympathy.api.exceptions import SyDataError
from sympathy.api.exceptions import SyNodeError

# from sylib.machinelearning.utility import array_to_table
# from sylib.machinelearning.utility import coerce_to_np
# from sylib.machinelearning.utility import data_to_table
# from sylib.machinelearning.utility import encode, decode
# from sylib.machinelearning.utility import find_dot
# from sylib.machinelearning.utility import names_from_x
# from sylib.machinelearning.utility import names_from_y
# from sylib.machinelearning.utility import table_to_array
# from sylib.machinelearning.utility import value_to_tables


def encode(obj):
    return base64.b64encode(pickle.dumps(obj)).decode('ascii')

def decode(unibytes_):
    return pickle.loads(base64.b64decode(unibytes_))

def table_to_array(tbl, unitary=False):
    result = np.array([tbl.get_column_to_array(colname) for colname in tbl.column_names()]).T
    if unitary and result.shape[1] == 1:
        result = result.reshape(result.shape[0])
    return result

def array_to_table(cols, arr, tbl=None):
    if tbl is None:
        tbl = table.File()
    for i, name in enumerate(cols):
        tbl.set_column_from_array(name, arr[:,i])
    return tbl

def find_dot():
    gviz_path=settings()['Debug/graphviz_path']
    dot = distutils.spawn.find_executable(vs.str_('dot'), gviz_path)
    if dot:
        return dot
    dot = distutils.spawn.find_executable(vs.str_('dot'))
    if dot:
        return dot
    else:
        return None

def data_to_table(X, names, table, default_prefix='x', transpose=False):
    """
    Writes the content of X into a sympathy table.

    2D Arrays keep their default shape (first index is table row, second column)
    lists are assumed to be lists of columns.
    """

    if scipy.sparse.issparse(X):
        X = X.toarray()

    def prepare_names(names, N):
        if len(names) < N:
            names = names + [
                '{}{}'.format(default_prefix, i)
                for i in range(len(names), N)]
        names = [str(name) for name in names]
        return names[:N]

    if isinstance(X, list):
        if X == []:
            return
        length = np.max([len(x) for x in X])
        if scipy.sparse.issparse(X[0]):
            X = [x.toarray() for x in X]
        if isinstance(X[0], list):
            X = [np.array(x) for x in X]
        if isinstance(X[0], np.ndarray) and len(X[0].shape) == 1:
            for i, x in enumerate(X):
                X[i] = np.r_[x,np.zeros(length-len(x), dtype=x.dtype)]
        else:
            raise SyDataError(
                'Cannot handle input of type [{}]'.format(type(X[0])))
        names = prepare_names(names, len(X))
        if transpose:
            table.set_column_from_array('feature', np.array(names))
            X = np.array(X)
            for i in range(X.shape[1]):
                table.set_column_from_array('r{}'.format(i), X[:,i])
        else:
            for name, col in zip(names, X):
                table.set_column_from_array(name, col)
        return X
    elif isinstance(X, np.ndarray):
        if len(X.shape) == 1:
            X = X.reshape((len(X), 1))
        names = prepare_names(names, X.shape[1])
        if transpose:
            table.set_column_from_array('feature', np.array(names))
            for i in range(X.shape[0]):
                table.set_column_from_array('r{}'.format(i), X[i,:])
        else:
            for i in range(X.shape[1]):
                table.set_column_from_array(names[i], X[:,i])
    else:
        raise SyDataError('Cannot handle input of type [{}]'.format(type(X)))

def names_from_x(desc, skl, *args):
    return desc.x_names

def names_from_y(desc, skl, *args):
    return desc.y_names

class _PickleablePrefixGeneratingFunction(object):
    """Dummy class that pretends to be a function with a lexical enclosure that cannot pickled, instead implemented
    as a class with explit storage of the enclosed value"""
    def __init__(self, prefix):
        self.prefix = prefix
    def __call__(self, desc, skl, *args):
        return lambda n: '{}{}'.format(self.prefix, n)

def names_from_prefix(prefix):
    return _PickleablePrefixGeneratingFunction(prefix)

def coerce_to_np(value):
    if (isinstance(value, list) and
        (value == [] or
         isinstance(value[0], numbers.Number) or
         isinstance(value[0], six.string_types))):
        return np.array(value)
    else:
        return value

def value_to_tables(value, name, cnames=None, rnames=None):
    """Attempts to convert a generic value to a list of tables.

    cnames are the column names used for 2D or 3D arrays.

    Handles:
      - scalars
      - 1D arrays
      - 2D arrays
      - 3D arrays
      - list of scalars
      - list of 1D arrays
      - list of 2D arrays
      - dictionary
    """

    out = []
    if isinstance(value, set):
        value = list(value)
    if (isinstance(value, list) and
        (value == [] or
         isinstance(value[0], numbers.Number) or
         isinstance(value[0], six.string_types))):
        value = np.array(value)

    if isinstance(value, str) or isinstance(value, numbers.Number):
        tbl = table.File()
        tbl.set_name(name)
        tbl.set_column_from_array(name, np.array([value]))
        out.append(tbl)
        return out
    elif isinstance(value, np.ndarray):
        dimensions = len(value.shape)
        if dimensions == 1 and cnames is not None:
            # Let column vectors become a row vector when column names are given
            value = value.reshape((1,)+value.shape)
            dimensions += 1

        if dimensions == 1:
            tbl = table.File()
            tbl.set_name(name)
            if rnames is not None:
                if callable(rnames):
                    rnames = [rnames(i) for i in range(value.shape[0])]
                tbl.set_column_from_array('name',np.array(rnames[:value.shape[0]]))
            tbl.set_column_from_array(name, value)
            return [tbl]
        elif dimensions == 2:
            tbl = table.File()
            tbl.set_name(name)
            if rnames is not None:
                if callable(rnames):
                    rnames = [rnames(i) for i in range(value.shape[0])]
                tbl.set_column_from_array('name',np.array(rnames[:value.shape[0]]))
            for col in range(value.shape[1]):
                if callable(cnames):
                    cname = cnames(col)
                elif cnames is None or value.shape[1] > len(cnames):
                    cname = "{}_{}".format(name, col)
                else:
                    cname = cnames[col]
                tbl.set_column_from_array(cname, value[:, col])
            out.append(tbl)
            return out
        elif dimensions == 3:
            for layer in range(value.shape[0]):
                tbl = table.File()
                tbl.set_name("{}_{}".format(name, layer))
                for col in range(value.shape[2]):
                    tbl.set_column_from_array(
                        "{}_{}_{}".format(name, layer, col),
                        value[layer, :, col])
                out.append(tbl)
            return out
    elif isinstance(value, list):
        for n in range(len(value)):
            tbl = table.File()
            tbl.set_name("{}_{}".format(name, n))
            val = coerce_to_np(value[n])
            if isinstance(val, np.ndarray):
                dimensions = len(val.shape)
                if dimensions == 1:
                    if callable(cnames):
                        cname = cnames(col)
                    if cnames is None or n > len(cnames):
                        cname = "{}_{}".format(name, n)
                    else:
                        cname = cnames[n]
                    tbl.set_column_from_array(cname, val)
                elif dimensions == 2:
                    # TODO - handle cnames or rnames
                    for col in range(val.shape[1]):
                        tbl.set_column_from_array(
                            "{}_{}_{}".format(
                                name, n, col), val[:, col])
                else:
                    raise SyNodeError('Invalid number of dimensions in {}'
                                      .format(name))
            elif isinstance(val, dict):
                tbl.set_name("{}".format(name))
                keys = np.array(list(val.keys()))
                values = np.array(list(val.values()))
                order = np.argsort(keys)
                tbl.set_column_from_array('key', keys[order])
                tbl.set_column_from_array('value', values[order])
            else:
                raise SyNodeError('Invalid datatype {} for {}'
                                  .format(type(value), name))
                return
            out.append(tbl)
        return out
    elif isinstance(value, dict):
        tbl = table.File()
        tbl.set_name("{}".format(name))
        keys = np.array(list(value.keys()))
        values = np.array(list(value.values()))
        order = np.argsort(keys)
        tbl.set_column_from_array('key', keys[order])
        tbl.set_column_from_array('value', values[order])
        out.append(tbl)
        return out
    elif value == None:
        return []
    else:
        raise SyDataError('Invalid datatype {} for {}'
                          .format(type(value), name))

