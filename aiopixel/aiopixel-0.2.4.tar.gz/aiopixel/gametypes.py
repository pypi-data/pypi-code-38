from enum import Enum


class GameType(Enum):
    """
    An enum of game types
    """

    # This is formatted the way it is for readability as if it were a table
    # much like the one at
    # https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/misc/GameType.md
    # Format:
    # Type name       ID  DB Name          Clean Name
    QUAKECRAFT     = (2,  "Quake",         "Quake")
    WALLS          = (3,  "Walls",         "Walls")
    PAINTBALL      = (4,  "Paintball",     "Paintball")
    SURVIVAL_GAMES = (5,  "HungerGames",   "Blitz Survival Games")
    TNTGAMES       = (6,  "TNTGames",      "TNT Games")
    VAMPIREZ       = (7,  "VampireZ",      "VampireZ")
    WALLS3         = (13, "Walls3",        "Mega Walls")
    ARCADE         = (14, "Arcade",        "Arcade")
    ARENA          = (17, "Arena",         "Arena")
    UHC            = (20, "UHC",           "UHC Champions")
    MCGO           = (21, "MCGO",          "Cops and Crims")
    BATTLEGROUND   = (23, "Battleground",  "Warlords")
    SUPER_SMASH    = (24, "SuperSmash",    "Smash Heroes")
    GINGERBREAD    = (25, "GingerBread",   "Turbo Kart Racers")
    HOUSING        = (26, "Housing",       "Housing")
    SKYWARS        = (51, "SkyWars",       "SkyWars")
    TRUE_COMBAT    = (52, "TrueCombat",    "Crazy Walls")
    SPEED_UHC      = (54, "SpeedUHC",      "Speed UHC")
    SKYCLASH       = (55, "SkyClash",      "SkyClash")
    LEGACY         = (56, "Legacy",        "Classic Games")
    PROTOTYPE      = (57, "Prototype",     "Prototype")
    BEDWARS        = (58, "Bedwars",       "Bed Wars")
    MURDER_MYSTERY = (59, "MurderMystery", "Murder Mystery")
    BUILD_BATTLE   = (60, "BuildBattle",   "Build Battle")
    DUELS          = (61, "Duels",         "Duels")
    SKYBLOCK       = (None, None, None)

    def __init__(self, _id: int, db_name: str, name: str):
        self.id = _id
        self.db_name = db_name
        self.clean_name = name

    @classmethod
    def from_id(cls, _id: int):
        for gt, data in cls.__members__.items():
            if _id == data.id:
                return data
        return None

    @classmethod
    def from_db_name(cls, db_name: str):
        for gt, data in cls.__members__.items():
            if db_name == data.db_name:
                return data
        return None

    @classmethod
    def from_clean_name(cls, clean_name: str):
        for gt, data in cls.__members__.items():
            if clean_name == data.clean_name:
                return data
        return None
