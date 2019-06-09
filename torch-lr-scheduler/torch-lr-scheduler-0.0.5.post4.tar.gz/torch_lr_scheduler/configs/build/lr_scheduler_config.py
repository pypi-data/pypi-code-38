from typing import List


class LrSchedulerConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.learning_rate_scale: float = values.get("learning_rate_scale", 1.0)
        self.line_chain: List[dict] = values.get("line_chain", [])
