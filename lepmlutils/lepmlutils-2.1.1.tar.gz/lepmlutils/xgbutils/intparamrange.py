from .floatparamrange import FloatParamRange

class IntParamRange(FloatParamRange):
    def value(self, index: int) -> int:
        return round(super().value(index))