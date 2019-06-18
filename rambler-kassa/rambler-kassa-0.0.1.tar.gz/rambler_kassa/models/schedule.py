from datetime import datetime

from pydantic import BaseModel


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
    MinPrice: str
    MaxPrice: str
    HallID: str
    HallName: str
    FeeType: str
    FeeValue: str

