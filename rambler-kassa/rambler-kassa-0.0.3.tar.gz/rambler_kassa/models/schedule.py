from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class Schedule(BaseModel):
    SessionID: int
    CityID: int
    CreationClassType: str
    CreationObjectID: int
    PlaceClassType: str
    PlaceObjectID: int
    DateTime: datetime
    Format: str
    IsSaleAvailable: bool
    IsReservationAvailable: bool
    IsWithoutSeats: bool
    MinPrice: Optional[int]
    MaxPrice: Optional[int]
    HallID: str
    HallName: str
    FeeType: str
    FeeValue: str

    @validator('MinPrice', 'MaxPrice', pre=True, whole=True)
    def str_to_int(cls, v):
        try:
            return int(v)
        except ValueError:
            return None
