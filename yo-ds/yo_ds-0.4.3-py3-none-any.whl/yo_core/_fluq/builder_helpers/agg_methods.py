import pandas as pd
import numpy as np
from yo_core._common import Obj
from .generics import KeyValuePair
from typing import *

def _or_default(with_default, default):
    if with_default:
        return default
    raise ValueError("Sequence contains no elements")


def first(en, with_default, default=None):
    for e in en:
        return e
    return _or_default(with_default, default)

def single(en, with_default, default=None):
    firstTime = True
    value = None
    for e in en:
        if firstTime:
            value = e
            firstTime = False
        else:
            raise ValueError('Sequence contains more than one element')
    if not firstTime:
        return value
    return _or_default(with_default, default)

def last(en, with_default, default=None):
    firstTime = True
    value = None
    for e in en:
        if firstTime:
            firstTime = False
        value = e
    if not firstTime:
        return value
    return _or_default(with_default, default)

def count(en):
    counter = 0
    for e in en:
        counter+=1
    return counter

def sum(en):
    result = 0
    for e in en:
        result+= e
    return result


def to_set(en):
    result = set()
    for e in en:
        if e in result:
            raise ValueError("Duplicating element {0}".format(e))
        result.add(e)
    return result


def to_ndarray(en):
    return np.array(list(en))

def to_dataframe(q, **kwargs):
    data = list(q)
    df = pd.DataFrame(data,**kwargs)
    if len(data)>0 and isinstance(data[0],Obj):
        columns = list(data[0].keys())
        df = df[columns]
    return df


class _KeyValueSelector:
    def __init__(self, keySelector: bool, allowNonKeyValue: bool):
        self.isFirstTime = True
        self.isKeyValuePairs = False
        self.keySelector = keySelector
        self.allowNonKeyValue = allowNonKeyValue

    def select(self, e):
        if self.isFirstTime:
            self.isFirstTime=False
            if isinstance(e,KeyValuePair):
                self.isKeyValuePairs = True
            else:
                self.isKeyValuePairs = False
        else:
            if isinstance(e,KeyValuePair)!=self.isKeyValuePairs:
                raise ValueError('Sequence was a mixture od KeyValuePair and something else, which is not allowed in this context')
        if self.isKeyValuePairs:
            if self.keySelector:
                return e.key
            else:
                return e.value
        else:
            if self.allowNonKeyValue:
                return e
            else:
                raise ValueError('Sequence was not of KeyValuePair')


def to_dictionary(en, key_selector, value_selector):
    if (key_selector is None) != (value_selector is None):
        raise ValueError('key_selector and value_selector must be provided either both or none')
    if key_selector is None and value_selector is None:
        key_selector = _KeyValueSelector(True,False).select
        value_selector = _KeyValueSelector(False,False).select
    result = {}
    for e in en:
        key = key_selector(e)
        if key in result:
            raise ValueError('Duplicating value for the key `{0}`'.format(key))
        value = value_selector(e)
        result[key]=value
    return result

def to_series(en, item_to_value, item_to_index):
    index = []
    values = []
    if item_to_value is None:
        item_to_value = _KeyValueSelector(False,True).select

    keySelectorObject = None # type: Optional[_KeyValueSelector]
    if item_to_index is None:
        keySelectorObject = _KeyValueSelector(True,True)
        item_to_index = keySelectorObject.select

    for e in en:
        values.append(item_to_value(e))
        index.append(item_to_index(e))

    if keySelectorObject is not None and not keySelectorObject.isKeyValuePairs:
        index = None

    return pd.Series(values,index)

