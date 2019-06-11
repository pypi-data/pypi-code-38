from typing import List


class ResNetConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", None)
        self.layers_list: List[int] = values.get("layers_list", [3, 4, 6, 3])
        self.stride_list: List[int] = values.get("stride_list", [2, 2, 1, 2, 2, 2])
        self.feature_dim: int = values.get("feature_dim", 1000)
        self.dropout_ratio: float = values.get("dropout_ratio", 0.0)
