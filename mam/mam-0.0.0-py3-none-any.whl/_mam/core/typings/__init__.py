"""Core typings."""

from __future__ import annotations

from typing import (
    Any, Dict, Tuple, Union,
)

# nosa(2): pylint[C0103]
ConfigObject = Any
Mutation = Any
MutationTree = Dict[str, Union[str, Any]]
Path = Tuple[str, ...]
