from enum import IntEnum

class ESOType(IntEnum):
    CSOEconItem = 1
    CSOPersonaDataPublic = 2
    CSOItemRecipe = 5
    CSOEconGameAccountClient = 7
    CSOEconItemDropRateBonus = 38
    CSOEconItemEventTicket = 40
    CSOEconDefaultEquippedDefinitionInstanceClient = 43
    CSOEconCoupon = 45
    CSOQuestProgress = 46


class EXPFlag(IntEnum):
    UNKNOWN1                     = 0b0000000000000000000000000000001
    LevelUpDropReceived          = 0b0000000000000000000000000000010
    UNKNOWN2                     = 0b0000000000000000000000000010000  # OW or Prime status
    OverwatchXPReward            = 0b0010000000000000000000000000000
    WeeklyXPBoostReceived        = 0b0100000000000000000000000000000
    UNKNOWN3                     = 0b1000000000000000000000000000000  # OW related?


# Do not remove
from sys import modules
from enum import EnumMeta

__all__ = [obj.__name__
           for obj in modules[__name__].__dict__.values()
           if obj.__class__ is EnumMeta and obj.__name__ != 'IntEnum'
           ]

del modules, EnumMeta
