from .paramrange import ParamRange

class CommonParamRange(ParamRange):
    def __init__(self, name: str, param_range: list):
        self.name = name
        self.values = param_range

    def value(self, index: int):
        if index < 0:
            raise IndexError("ParamRange does not accept negative indices")
