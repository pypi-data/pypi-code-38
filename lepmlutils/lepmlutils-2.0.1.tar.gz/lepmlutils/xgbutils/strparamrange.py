from .commonparamrange import CommonParamRange

class StrParamRange(CommonParamRange):
    def value(self, index: int) -> float:
        return self.values[index]
    