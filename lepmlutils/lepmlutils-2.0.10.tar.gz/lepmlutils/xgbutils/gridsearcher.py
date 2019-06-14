from .commonsearcher import CommonSearcher
from typing import Dict

class GridSearcher(CommonSearcher): 
    def __next__(self) -> Dict:
        current_params = {}
        value_indices = next(self.perms)
        for index, key in enumerate(self.params.keys()):
            current_params[key] = self.params[key][value_indices[index]]

        return current_params                  