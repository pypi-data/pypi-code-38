from .fluq_initiators import FileQuery as _FileQuery, CombinatoricsQuery as _CombinatoricsQuery, folder as _folder
from yo_core import *
from yo_core import Query as QueryBase
from pathlib import Path

from . import alg, fluq, plots

class Query(QueryBase):
    file = _FileQuery()
    combinatorics = _CombinatoricsQuery()
    @staticmethod
    def folder(location: Union[Path, str], pattern: str = '*') -> Queryable[Path]:
        return Queryable(_folder(location, pattern))
