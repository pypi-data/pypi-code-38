import os
from typedresult.result import Result

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

updated_version = "v0.0.0"

if updated_version == "v0.0.0":
    __version__ = "0.0.0"
else:
    __version__ = updated_version

classes = [
    "Result",
]

__all__ = classes