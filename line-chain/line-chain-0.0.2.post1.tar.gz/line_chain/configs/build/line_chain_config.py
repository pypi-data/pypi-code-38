from typing import List


class Line:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.mode: str = values.get("mode", 'fixed')
        self.start: float = values.get("start", None)
        self.target: float = values.get("target", 0.0)
        self.ratio: float = values.get("ratio", 1.0)


class LineChainConfig:
    def __init__(self, values: list = None):
        values = values if values is not None else []
        self.items: List[Line] = [
            Line(values=value) for value in values
        ]
