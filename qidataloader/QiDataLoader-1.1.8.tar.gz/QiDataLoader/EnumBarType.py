from enum import Enum,unique

@unique
class EnumBarType(Enum):
    Tick = 0,
    Second = 1,
    Minute = 2,
    Hour = 3,
    Day = 4,
    Week = 5,
    Month = 6,
    Year= 7