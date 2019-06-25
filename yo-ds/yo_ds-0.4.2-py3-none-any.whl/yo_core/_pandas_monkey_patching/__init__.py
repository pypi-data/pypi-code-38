import pandas as pd
from typing import *

T = TypeVar('T')
TOut = TypeVar('TOut')

def _feed(object: T, method: Callable[[T],TOut])->TOut:
    return method(object)


pd.Series.feed = _feed
pd.DataFrame.feed = _feed
pd.core.groupby.DataFrameGroupBy.feed = _feed
pd.core.groupby.SeriesGroupBy.feed = _feed
