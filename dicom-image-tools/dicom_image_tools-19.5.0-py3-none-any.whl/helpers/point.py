from dataclasses import dataclass
from typing import Dict, Optional, Union


@dataclass
class Point:
    x: float
    y: float
    z: Optional[float] = None


@dataclass
class IntPoint:
    x: int
    y: int
    z: Optional[int] = None


CenterPosition = Union[Point, Dict[str, float]]
