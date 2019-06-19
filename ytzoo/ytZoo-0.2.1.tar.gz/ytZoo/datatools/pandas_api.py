from .pandas_flavor import register_dataframe_accessor
from functools import wraps
from collections import OrderedDict
import pandas as pd

@register_dataframe_accessor('bs')
class DataFrameBooster:
    def __init__(self, obj):
        self._obj = obj

def register_dataframe_booster(name):
    def decorator(f):
        # hack
        @wraps(f)
        def wrapper(*args, **kwargs):
            instance = args[0]
            args = args[1:]
            return f(instance._obj, *args, **kwargs)
        setattr(DataFrameBooster, name, wrapper)
        return f
    return decorator


@register_dataframe_accessor('fm')
class FilterManager:
    """Manage boolean-array filters.
    
    """
    def __init__(self, obj):
        self._obj = obj
        self.__filters = OrderedDict()

    def add(self, msk, name):
        self.__filters[name] = msk

    def show(self):
        return self.__filters.keys()

    def combine(self):
        msk = pd.concat(self.__filters.values(), axis=1)
        return msk.all(axis=1)

    def clear(self):
        self.__filters = OrderedDict()

    def waterfall(self):
        """Show how base is reduced through each filter."""
        r = []
        totobs = self._obj.shape[0]
        r.append({'name': 'Base',
                  'nobs': totobs,
                  '%R': '',
                  '%T': ''})
        lastobs = totobs
        lastmsk = pd.Series([True]*self._obj.shape[0], index=self._obj.index)
        for name, msk in self.__filters.items():
            cursel = lastmsk & msk
            nobs = cursel.sum()
            r.append({'name': name,
                      'nobs': nobs,
                      '%R': nobs/lastobs,
                      '%T': nobs/totobs})
            lastobs = nobs
            lastmsk = cursel
        df = pd.DataFrame(r)
        df = df[['name', 'nobs', '%R', '%T']]
        return df

    def reduce(self):
        """Return records that pass all filters"""
        return self._obj.loc[self.combine()]

    def reduce_index(self):
        return self.reduce().index
