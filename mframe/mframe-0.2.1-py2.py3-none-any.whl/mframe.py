import operator
import types
import datetime as dt


def parse_date(sdt):
    if isinstance(sdt, dt.datetime):
        return sdt
    # Limited support to guess datetime formats
    patterns = [
        '%Y-%m-%d', '%Y-%d-%m', '%d-%m-%Y',
        '%Y-%m-%d %H:%M:%S',
        # ISO 8601, offset (%z) not supported in Jython :(
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y%m%dT%H%M%SZ',
    ]
    for pattern in patterns:
        try:
            return dt.datetime.strptime(sdt, pattern)
        except:
            pass
    raise TypeError("{} is not a recognized datetime format".format(sdt))


class Series:
    __slots__ = ['data', 'dtype']

    def __init__(self, data):
        self.data = data
        self.dtype = self._dtype()

    def _dtype(self):
        if len(self) > 0 and isinstance(self.data[0], dt.datetime):
            return 'datetime'
        else:
            return 'object'

    def __iter__(self):
        return iter(self.data)

    def _dt_conversion(self, other):
        if isinstance(other, list):
            _other = []
            for o in other:                
                _other.append(parse_date(o))
            return _other
        else:
            return parse_date(other)

    def _compare(self, other, op):
        if self.dtype == 'datetime':
            other = self._dt_conversion(other)
        if isinstance(other, list):
            return op(self.data, other)
        else:
            values = []            
            for data in self.data:
                values.append(op(data, other))            
            return Series(values)

    def apply(self, fn):
        _values = []
        for value in self.data:
            _values.append(fn(value))
        self.data = _values
        return Series(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def __eq__(self, other):
        return self._compare(other, operator.eq)

    def __ge__(self, other):
        return self._compare(other, operator.ge)

    def __gt__(self, other):
        return self._compare(other, operator.gt)

    def __le__(self, other):
        return self._compare(other, operator.le)

    def __lt__(self, other):
        return self._compare(other, operator.lt)

    def __and__(self, other):
        combination = []
        for b1, b2 in zip(self.data, other):
            combination.append(all([b1, b2]))
        return Series(combination)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)


class DataFrame(object):
    # As the dataframe object does not allow setting columns via
    # attribute access, we take some pre-cautions to prevent it 
    # happening accidently.
    __slots__ = ['data', '_values', '_columns', '_selected_column'] # Python 3  

    # __slots__ not supported in Jython
    def _slot(self, attr, value): 
        super(DataFrame, self).__setattr__(attr, value)

    def __setattr__(self, name, value):
        raise AttributeError('{} is an unknown attribute'.format(name))
    #########

    def __init__(self, data=None, values=None, columns=None):
        if data is not None:
            self._slot('data', data)
            # TODO Test shape
            self._slot('_values', list(data.values()))
            self._slot('_columns', list(data.keys()))
        else:
            self._slot('_values', values)
            self._slot('_columns', columns)

    def get(self, column):
        if isinstance(column, Series): # Filter
            _vals = [[] for _ in range(len(self._values))] # Empty list of lists
            for i, value in enumerate(column):
                if value:
                    for j, value in enumerate(self._values):
                        _vals[j].append(value[i])
            return DataFrame(values=_vals, columns=self._columns)        

        idx = self._columns.index(column)
        return Series(self._values[idx])

    def _get_row_filter(self, mask):
        if isinstance(mask, str) and mask == 'all':
            return [True]*len(self)
        if isinstance(mask[0], list):
            _index = []
            for items in zip(*mask):
                if all(items):
                    _index.append(True)
                else:
                    _index.append(False)
            mask = _index   
        return mask

    def set(self, mask, column, value):        
        mask = self._get_row_filter(mask)
        _values = []       
        try:
            idx = self._columns.index(column)
        except ValueError: # Add New Column
            self._columns.append(column)
            idx = self._columns.index(column)
            self._values.append([None]*len(self))
        
        for i, (should_apply, current_value) in enumerate(zip(mask, self._values[idx])):
            if should_apply:
                if isinstance(value, (Series, list)):
                    _values.append(value[i])
                else:                    
                    _values.append(value)
            else:
                _values.append(current_value)
        self._values[idx] = _values            
                
    def iterrows(self):
        for i in range(len(self)):
            row = {}
            for j in range(len(self._columns)):
                row[self._columns[j]] = self._values[j][i]
            yield row

    def to_dict(self):
        d = {}
        for idx, column in enumerate(self._columns):
            d[column] = self._values[idx]
        return d
    
    def to_pandas(self):
        import pandas
        return pandas.DataFrame(self.to_dict())

    @property
    def pd(self):
        return self.to_pandas()

    def head(self, num=5):
        from tabulate import tabulate
        cut_values = zip(*[v[:num] for v in self._values])
        return tabulate(cut_values, headers=self._columns)

    def tail(self, num=5):
        from tabulate import tabulate
        cut_values = zip(*[v[len(v)-num:] for v in self._values])
        return tabulate(cut_values, headers=self._columns)

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, value):
        self.set('all', name, value)

    def __getattr__(self, name):
        return self.get(name)

    def __len__(self):
        return len(self._values[0])
        
    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return str(self.to_dict())
