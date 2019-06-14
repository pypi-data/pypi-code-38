class ArcFaceConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", None)
        self.feature_dim: int = values.get("feature_dim", None)
        self.num_classes: int = values.get("num_classes", None)
        self.s: float = values.get("s", 64.0)
        self.m: float = values.get("m", 0.5)
