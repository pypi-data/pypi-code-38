# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Feather data format reader

After https://arrow.apache.org/docs/python/_modules/pyarrow/feather.html
"""
from pyarrow.lib import FeatherReader, DictionaryType
import numpy as np

from .._data_obj import Dataset, Factor, Var


class Reader(FeatherReader):

    def __init__(self, source):
        self.source = source
        self.open(source)
        FeatherReader.__init__(self)

    def read(self, columns=None):
        if columns is not None:
            column_set = set(columns)
        else:
            column_set = None

        ds = Dataset()
        for i in range(self.num_columns):
            name = self.get_column_name(i)
            if column_set is None or name in column_set:
                col = self.get_column(i)
                if len(col.shape) != 1:
                    raise IOError(
                        "%s: reading multidimensional columns not currently "
                        "supprted (try skipping column %r)" %
                        (self.source, name))
                n = col.length()
                data = (col.data[i].as_py() for i in range(n))
                if isinstance(col.type, DictionaryType) or col.type.equals('string'):
                    ds[name] = Factor(data)
                else:
                    data = np.fromiter(data, col.type.to_pandas_dtype(), n)
                    ds[name] = Var(data)

        return ds
