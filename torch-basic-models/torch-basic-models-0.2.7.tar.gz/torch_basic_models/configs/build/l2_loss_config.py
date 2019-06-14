class L2LossConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.type: str = values.get("type", None)
        self.normalize: bool = values.get("normalize", False)
