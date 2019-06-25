import pandas as pd
from .._common import Obj
from .query_builder import Queryable
from typing import *
from .builder_helpers.generics import TKey, TValue, KeyValuePair

T = TypeVar('T')


def _df_iter(dataframe):
    for row in dataframe.iterrows():
        yield Obj(**row[1].to_dict())


class Query:
    @staticmethod
    def en(en: Iterable[T]) -> Queryable[T]:
        length = None
        if hasattr(en,'__len__'):
            length = len(en)
        return Queryable(en, length)

    @staticmethod
    def dict(dict: Dict[TKey,TValue])->Queryable[KeyValuePair[TKey,TValue]]:
        return Queryable(
            map(lambda z: KeyValuePair(z[0],z[1]), dict.items()),
            len(dict)
        )

    @staticmethod
    def series(series: pd.Series) -> Queryable[KeyValuePair]:
        return Queryable(
            map(lambda z: KeyValuePair(z[0],z[1]), zip(series.index,series)),
            series.shape[0]
        )


    @staticmethod
    def args(*args: T) -> Queryable[T]:
        return Queryable(args, len(args))


    @staticmethod
    def df(dataframe: pd.DataFrame):
        return Queryable(_df_iter(dataframe), dataframe.shape[0])







