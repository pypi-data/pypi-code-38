"""Common mutations typings."""

from typing import (
    Any, Dict, Union,
)

from ...core.objects import _Null

TNone = Union[_Null, None]
Task = Dict[str, Any]
