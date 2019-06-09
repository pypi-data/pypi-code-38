from typing import List


class OptimizerConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", 'SGD')
        self.lr: float = values.get("lr", 0.0)
        self.kwargs: dict = values.get("kwargs", {})
        self.rules: List[dict] = values.get("rules", [{}])
