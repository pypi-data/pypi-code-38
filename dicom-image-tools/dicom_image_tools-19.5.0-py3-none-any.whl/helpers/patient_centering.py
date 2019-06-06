from dataclasses import dataclass
from typing import Optional


@dataclass
class PatientMassCenter:
    x: float
    y: float
    z: Optional[float] = None


@dataclass
class PatientGeometricalOffset:
    x: float
    y: float
