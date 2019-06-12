from typing import Dict, List
from .commonsearcher import CommonSearcher
from .paramrange import ParamRange
from .intparamrange import IntParamRange
from .floatparamrange import FloatParamRange
from .strparamrange import StrParamRange

# RandGridSearcher is aimed at exploring the hyperparameter 
# space more effectively than grid search by making each
# hyperparameter value somewhat random. In particular no
# hyperparameter value should be repeated. 
class RandGridSearcher(CommonSearcher):
    def __init__(self, params: Dict):
        super().__init__(params)
        self.ranges = {}
        for name, values in params.items():
            self.ranges[name] = self.range_for(name, values)


    def range_for(self, name: str, values: list) -> ParamRange:
        value = values[0]
        if type(value) == int:
            return IntParamRange(name, values)
        if type(value) == float:
            return FloatParamRange(name, values)
        else:
            return StrParamRange(name, values)

    def __next__(self) -> Dict:
        current_params = {}
        value_indices = next(self.perms)
        for index, key in enumerate(self.ranges.keys()):
            current_params[key] = self.ranges[key].value(value_indices[index])

        return current_params   
        
