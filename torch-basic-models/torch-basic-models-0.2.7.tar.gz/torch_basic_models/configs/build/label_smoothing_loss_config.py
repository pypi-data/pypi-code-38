class LabelSmoothingLossConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", None)
        self.smooth_ratio: float = values.get("smooth_ratio", 0.1)
