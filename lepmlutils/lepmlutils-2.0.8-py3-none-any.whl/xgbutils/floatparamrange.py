import random
from typing import List
from typing import List

from .commonparamrange import CommonParamRange

class FloatParamRange(CommonParamRange):
    PRECISION = 10

    def value(self, index: int) -> float:
        super().value(index)
        return self.range_for(index)
    
    def range_for(self, index: int):
        base_value = self.values[index]

        if index == 0:
            lower_bound = base_value
        else:
            lower_val = self.values[index - 1]
            lower_bound = lower_val + 0.5 * (base_value - lower_val)
        
        if index >= len(self.values) - 1:
            upper_bound = base_value
        else:
            upper_val = self.values[index + 1]
            upper_bound = upper_val - 0.5 * (upper_val - base_value)
        
        return lower_bound + self.portion(lower_bound, upper_bound)
        
    def portion(self, lower_bound: float, upper_bound: float) -> float:
        return ((upper_bound - lower_bound) / FloatParamRange.PRECISION) * random.randint(1, FloatParamRange.PRECISION - 1)