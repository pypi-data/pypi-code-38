from typing import List


class StateFile:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.config: dict = values.get("config", None)
        self.model: dict = values.get("model", None)
        self.optimizers: List[dict] = values.get("optimizers", [])
        self.info: dict = values.get("info", None)
        self.timestamp: str = values.get("timestamp", None)
