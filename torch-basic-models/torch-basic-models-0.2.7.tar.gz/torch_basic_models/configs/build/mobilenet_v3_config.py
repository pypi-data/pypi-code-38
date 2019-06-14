from typing import List


class MobileNetV3Config:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", None)
        self.feature_dim: int = values.get("feature_dim", 1000)
        self.width_multiple: float = values.get("width_multiple", 1.0)
        self.dropout_ratio: float = values.get("dropout_ratio", 0.0)
        self.stride_list: List[int] = values.get("stride_list", [2, 2, 2, 2, 2])
