from .searcher import Searcher
from typing import Dict
import itertools

class CommonSearcher(Searcher):
    def __init__(self, params: Dict):
        self.params = params
        index_lists = []
        for lst in params.values():
            index_lists.append(list(range(0, len(lst))))       
        self.perms = itertools.product(*index_lists)
        
    def __iter__(self) -> Searcher:
        return self               