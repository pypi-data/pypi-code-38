#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
"""
Pandas
------
"""
import logging
import pandas as pd
from pathlib import Path
from .._base import *

__all__ = ['PandasParser']
log = logging.getLogger(__name__)


class PandasParser(Parser):
    """ This parser can be used to read and write to any format that is supported by pandas,
    through its ``to_*`` and ``read_*`` functions. See the pandas `IO Documentation`_ for more information about the formats.
    This parser adds some logic on top to return dataframes with correct column types
    and allows these formats to be used by all brambox scripts and tools.

    Args:
        pd_format (string): Which format to save as. This string must match with whatever comes after ``to_``/``read_`` in the function names; Default **Infer from file extension**
        kwargs: Extra keyword arguments that are passed on to the pandas IO function; Default **See r_defaults and w_defaults**

    Note:
        If you do not pass a `pd_format` argument, it will be inferred from the file extension. |br|
        Below is a list of extensions that are matched with a certain format. |br|
        Note that not all supported pandas formats are listed.
        Only formats that were able to save and load the dataframes correctly were added to this list.
        *(See warning for more information)*

        .. dict:: brambox.io.parser.box PandasParser extension

    Note:
        In order to correctly (de)serialize the annotations and detections,
        we provide default arguments for some of the formats.
        These default values can be overwritten by providing your own through the keyword arguments!

        .. dict:: brambox.io.parser.box PandasParser r_defaults
        .. dict:: brambox.io.parser.box PandasParser w_defaults

    Warning:
        Some of these formats cannot correctly save categorical data.
        This means the images column will be saved as a regular string column
        and thus all images that do not contain bounding boxes will be lost!

        .. exec::
           import brambox as bb
           print('The following formats are unsafe: ' + str(bb.io.parser.box.PandasParser.unsafe_formats))

    .. _IO Documentation: https://pandas.pydata.org/pandas-docs/stable/io.html
    """
    parser_type = ParserType.EXTERNAL
    unsafe_formats = ('csv', 'json', 'html', 'excel', 'parquet', 'sql')
    extension = {
        '.csv': 'csv',
        '.tsv': 'csv',
        '.json': 'json',
        '.html': 'html',
        '.xls': 'excel',
        '.xlsx': 'excel',
        '.hdf': 'hdf',
        '.hdf5': 'hdf',
        '.h5': 'hdf',
        '.he5': 'hdf',
        '.parquet': 'parquet',
        '.msgpack': 'msgpack',
        '.pkl': 'pickle',
        '.pck': 'pickle',
    }
    w_defaults = {
        'csv': {'index_label': 'index'},
        'hdf': {'key': 'df', 'format': 'table'},
        'excel': {'index': False},
    }
    r_defaults = {
        'csv': {'index_col': 0},
        'json': {'dtype': {'x_top_left': 'float64', 'y_top_left': 'float64', 'width': 'float64', 'height': 'float64', 'occluded': 'float64', 'truncated': 'float64', 'confidence': 'float64'}},
        'html': {'index_col': 0},
        'excel': {'dtype': {'x_top_left': 'float64', 'y_top_left': 'float64', 'width': 'float64', 'height': 'float64', 'occluded': 'float64', 'truncated': 'float64', 'confidence': 'float64'}},
    }

    def __init__(self, pd_format=None, **kwargs):
        self.format = pd_format
        self.kwargs = kwargs

        if self.format in self.unsafe_formats:
            log.error(f'Saving as {self.format} does not retain categorical dtypes! You will thus lose all images that have no boxes.')
        if self.format is None:
            log.warning("No 'pd_format' argument found, inferring format from file extension")

    def _infer_format(self, path):
        ext = Path(path).suffix

        try:
            self.format = self.extension[ext]
            log.debug(f"Inferred Pandas format as '{self.format}' from file extension [{ext}]")
            if self.format in self.unsafe_formats:
                log.error(f'Saving as {self.format} does not retain categorical dtypes! You will thus lose all images that have no boxes.')
        except KeyError as err:
            raise TypeError(f"[{ext}] is not a known file extension. Please provide a format manually with the 'pd_format' argument") from err

    def serialize(self, df, path):
        if self.format is None:
            self._infer_format(path)
        method_name = f'to_{self.format}'
        defaults = self.w_defaults.get(self.format, {})

        try:
            getattr(df, method_name)(path, **{**defaults, **self.kwargs})
        except AttributeError as err:
            raise NotImplementedError(f'{method_name} is not a valid function of a pandas dataframe') from err

    def deserialize(self, path):
        if self.format is None:
            self._infer_format(path)
        method_name = f'read_{self.format}'
        defaults = self.r_defaults.get(self.format, {})

        try:
            self.data = getattr(pd, method_name)(path, **{**defaults, **self.kwargs})
        except AttributeError as err:
            raise NotImplementedError(f'{method_name} is not a valid function in pandas') from err

        if isinstance(self.data, list):
            self.data = self.data[0]

        if self.data.image.dtype.name != 'category':
            self.data.image = self.data.image.astype('category')

        if not self.data.index.is_monotonic_increasing:
            self.data = self.data.sort_index()
