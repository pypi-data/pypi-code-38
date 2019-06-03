from pathlib import Path
from typing import Union


class InputData:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
