import pandas as pd
import io
import json
import numpy as np
import pickle
import warnings
import logging


def header_wrapper(func):
    def wrapper(*args, **kwargs):
        first_arg = args[0]
        if isinstance(first_arg, DataContainer):
            header = first_arg.header
        elif isinstance(first_arg, list):
            for item in first_arg:
                if isinstance(item, DataContainer):
                    header = item.header
        for arg in args:
            header = _combine_header(header, arg)
        dataframe = func(*args, **kwargs)
        if isinstance(dataframe, (pd.DataFrame, pd.Series)):
            return DataContainer(dataframe, header=header)
        elif isinstance(dataframe, type(None)):
            first_arg.header = header
            return
        else:
            raise TypeError('Not a DataFrame like object.')

    return wrapper


def wrapper_factory(function, base):
    if function in base.__dict__:
        @header_wrapper
        def wrapped_function(self, *args, **kwargs):
            return base.__dict__[function](self, *args, **kwargs)

        docstring = base.__dict__[function].__doc__
    elif function in base.__bases__[0].__dict__:
        @header_wrapper
        def wrapped_function(self, *args, **kwargs):
            return base.__bases__[0].__dict__[function](self, *args, **kwargs)

        docstring = base.__bases__[0].__dict__[function].__doc__
    else:
        raise KeyError('No function called \'{0}\' in original functions from {1}'.format(function, base))
    return wrapped_function, docstring


class MetaDataContainer(type):
    magic_methods = ['__add__', '__sub__', '__mul__', '__floordiv__', '__truediv__', '__mod__', '__pow__',
                     '__and__', '__xor__', '__or__',
                     '__iadd__', '__isub__', '__imul__', '__ifloordiv__', '__itruediv__', '__imod__', '__ipow__',
                     '__iand__', '__ixor__', '__ior__',
                     ]
    single_parameter_magic_methods = ['__neg__', '__abs__', '__invert__']
    binary_operator = ['add', 'sub', 'mul', 'div', 'divide', 'truediv', 'floordiv', 'mod', 'pow', 'dot',
                       'radd', 'rsub', 'rmul', 'rdiv', 'rtruediv', 'rfloordiv', 'rmod', 'rpow']
    combining = ['append', 'join', 'merge', 'combine', 'combine_first']
    conversion = ['astype', 'infer_objects', 'copy', 'isna', 'notna', 'isnull', 'select_dtypes']
    indexing = ['isin', 'where', 'mask', 'query']
    function_application = ['apply', 'applymap', 'agg', 'aggregate', 'transform']
    computations_single = ['abs', 'clip', 'compound', 'corr', 'cov',
                           'cummax', 'cummin', 'cumprod', 'cumsum', 'describe', 'diff', 'kurt', 'kurtosis', 'mad',
                           'max', 'mean', 'median', 'min', 'mode', 'pct_change', 'prod', 'product', 'quantile', 'rank',
                           'round', 'sem', 'skew', 'sum', 'std', 'var', 'nunique']
    computations = ['clip_lower', 'clip_upper', 'corrwith', 'eval']
    reindexing = ['add_prefix', 'add_suffix', 'at_time', 'between_time', 'drop', 'drop_duplicates', 'filter', 'first',
                  'last', 'reindex', 'reindex_axis', 'reindex_like', 'rename', 'rename_axis', 'reset_index',
                  'sample', 'set_axis', 'set_index', 'take', 'truncate']
    missing_data = ['dropna', 'fillna', 'replace', 'interpolate']
    reshaping = ['pivot', 'pivot_table', 'reorder_levels', 'sort_values', 'sort_index', 'nlargest', 'nsmallest',
                 'swaplevel', 'stack', 'unstack', 'swapaxes', 'melt', 'squeeze', 'transpose']
    time_series = ['asfreq', 'asof', 'shift', 'slice_shift', 'tshift', 'to_period', 'to_timestamp', 'tz_convert',
                   'tz_localize']
    normal_methods = binary_operator + combining + conversion + indexing + function_application + computations + \
                     reindexing + missing_data + reshaping + time_series
    functions = normal_methods + magic_methods + single_parameter_magic_methods + computations_single

    def __new__(cls, name, bases, clsdict):
        base = bases[0]
        for function in MetaDataContainer.functions:
            clsdict[function], docstring = wrapper_factory(function, base)
            if isinstance(docstring, str):
                docstring = docstring.replace('DataFrame', 'DataContainer')
                docstring = docstring.replace('dataframe', 'DataContainer')
                docstring = docstring.replace('pd.DataContainer', 'DataContainer')
                docstring = docstring.replace('frame\'s', 'DataContainer\'s')
            clsdict[function].__doc__ = docstring
        return super().__new__(cls, name, bases, clsdict)


class DataContainer(pd.DataFrame, metaclass=MetaDataContainer):
    """
    DataContainer inherits from pandas.DataFrame and works with header variable to store additional information
    besides plain data.
    """

    general_keys = ['xUnit', 'yUnit', 'Date']
    keys = {
        'spectrum': ['RBW', 'VBW', 'Span', 'CenterFrequency'] + general_keys,
        'osci': general_keys
    }
    json_prefix = '-----DataContainerHeader\n'
    json_suffix = '-----DataContainerData\n'

    def __init__(self, *args, header=None, type=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._type = type
        if args:
            data = args[0]
        else:
            data = kwargs.get('data')

        with warnings.catch_warnings():  # pandas otherwise gives userwarning
            warnings.simplefilter("ignore")
            if header:
                if isinstance(header, dict):
                    self.header = header
                else:
                    raise TypeError('argument \'header\' must be a dict!')
            else:
                if isinstance(data, DataContainer):
                    self.header = data.header
                elif type:
                    try:
                        self._header_from_keys()
                    except KeyError:
                        raise TypeError('\"{0}\" is not a valid _type for DataContainer'.format(type))
                else:
                    self.header = dict()

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        if isinstance(header, dict):
            self._header = header
        else:
            raise TypeError('header variable must be a dict!')

    def __str__(self):
        header_string = ''
        for key in self.header:
            header_string += '{0} : {1}\n'.format(key, self.header[key])
        maxlen = 60
        length = maxlen  # if (maxlen < len(header_string)) else len(header_string)
        string = '-' * length + '\n' + header_string + '-' * length + '\n' + super().__str__()

        return string

    def __getitem__(self, key):
        header = self.header
        output = super().__getitem__(key)
        if isinstance(output, pd.DataFrame):
            output = DataContainer(output, header=header)
        elif isinstance(output, pd.Series):
            pass
        return output

    def head(self, n=5):
        header = self.header
        return DataContainer(super().head(n), header=header)

    def tail(self, n=5):
        header = self.header
        return DataContainer(super().tail(n), header=header)

    def _header_from_keys(self):
        self.header = dict.fromkeys(DataContainer.keys[self._type])

    @staticmethod
    @header_wrapper
    def concat(*args, **kwargs):
        return pd.concat(*args, **kwargs)

    def update_header(self, other):
        if not isinstance(other, dict):
            raise TypeError('argument for function must be dict like')
        else:
            self.header = {**self.header, **other}
        empty_keys = self.emtpy_keys()
        if empty_keys:
            print('Could not determine values for {0}'.format('\'' + ','.join(empty_keys) + '\''))

    def emtpy_keys(self):
        empty = []
        for key in self.header:
            if self.header[key] is None:
                empty.append(key)
        return empty

    def to_csv(self, path_or_buf=None, mode='w', *args, **kwargs):
        try:
            with open(path_or_buf, mode=mode) as file:
                self._to_csv(file, *args, **kwargs)
                # logging.debug('can open file!')
        except TypeError as e:
            logging.debug('got type error {}'.format(e))
            file = path_or_buf
            self._to_csv(file, *args, **kwargs)

    def _to_csv(self, file, *args, **kwargs):
        header = kwargs.get('header', True)
        if header:
            file.write(self._header_to_json())
        super().to_csv(*args, path_or_buf=file, **kwargs)

    @staticmethod
    def from_csv(file, *args, index_col=0, **kwargs):
        with open(file, 'r') as f:
            header_dict = DataContainer._json_to_header(f)
            output = DataContainer(pd.read_csv(f, *args, index_col=index_col, **kwargs), header=header_dict)
        return output

    def to_json(self, path_or_buf=None, *args, orient='split', **kwargs):
        if isinstance(path_or_buf, io.IOBase):
            file = path_or_buf
            self._to_json(file, *args, orient=orient, **kwargs)
        elif isinstance(path_or_buf, str):
            with open(path_or_buf, 'w') as file:
                self._to_json(file, *args, orient=orient, **kwargs)
        elif path_or_buf is None:
            with io.StringIO() as f:
                self._to_json(f, *args, orient=orient, **kwargs)
                return f.getvalue()
        else:
            raise ValueError('path_or_buf should be something useful.')

    def _to_json(self, file, *args, **kwargs):
        file.write(self._header_to_json())
        super().to_json(*args, path_or_buf=file, **kwargs)

    @staticmethod
    def from_json(file, *args, orient='split', **kwargs):
        if (file[0:2] == '{"' and file[-1] == '}') or file.startswith('-----'):
            handler = io.StringIO
        else:
            handler = open

        with handler(file) as f:
            header = DataContainer._json_to_header(f)
            output = DataContainer(pd.read_json(f, *args, orient=orient, **kwargs), header=header)
        return output

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d

    def _header_to_json(self):
        prefix = DataContainer.json_prefix
        suffix = DataContainer.json_suffix
        try:
            header_string = prefix + json.dumps(self.header) + '\n' + suffix
        except TypeError as e:
            raise TypeError(e.__str__() + '. Remove it in order to save to file')
        return header_string

    @staticmethod
    def _json_to_header(f):
        prefix = DataContainer.json_prefix
        suffix = DataContainer.json_suffix
        first = f.readline()
        header = f.readline().strip()
        last = f.readline()

        if not (first == prefix and last == suffix):
            f.seek(0)
            header = None
        else:
            header = json.loads(header)
        return header

    def plot(self, *args, **kwargs):
        plotter = pd.DataFrame.plot(self)
        ax = plotter(*args, **kwargs)
        xUnit = self.header.get('xUnit')
        if xUnit:
            xlabel = '{0} ({1})'.format(self.index.name, xUnit)
            if isinstance(ax, np.ndarray):
                ax[-1].set_xlabel(xlabel)
            else:
                ax.set_xlabel(xlabel)
        return ax


def _combine_header(header, other):
    if isinstance(other, list):
        itemlist = other[:]  # otherwise also other would be affectec by itemlist.pop()
        while itemlist:
            item = itemlist.pop()
            if isinstance(item, DataContainer):
                header = _combine_header(header, item.header)
            elif isinstance(item, dict):
                header = _combine_header(header, item)
            else:
                pass
                # raise TypeError('{0} has no attribute \"header\"'.format(type(item)))
    elif isinstance(other, DataContainer):
        header = _combine_header(header, other.header)
    elif isinstance(other, dict):
        d = dict()
        for key in header.keys() & other.keys():
            if header[key] == other[key]:
                d.update({key: header[key]})
        header = d
    return header
