from ..gametypes import GameType

__all__ = [
    "PlayerStats", "QuakeStats", "WallsStats", "PaintballStats",
    "HungerGamesStats", "TNTGamesStats", "VampireZStats", 
    "Walls3Stats", "ArcadeStats", "ArenaStats", "UHCStats", 
    "MCGOStats", "BattlegroundStats", "SuperSmashStats", 
    "GingerBreadStats", "HousingStats", "SkyWarsStats", 
    "TrueCombatStats", "SpeedUHCStats", "SkyClashStats", 
    "LegacyStats", "PrototypeStats", "BedwarsStats", 
    "MurderMysteryStats", "BuildBattleStats", "DuelsStats"
]

class PlayerStats:
    def __init__(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)


class QuakeStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.QUAKECRAFT
        super().__init__(data)


class WallsStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.WALLS
        super().__init__(data)


class PaintballStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.PAINTBALL
        super().__init__(data)


class HungerGamesStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.SURVIVAL_GAMES
        super().__init__(data)


class TNTGamesStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.TNTGAMES
        super().__init__(data)


class VampireZStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.VAMPIREZ
        super().__init__(data)


class Walls3Stats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.WALLS3
        super().__init__(data)


class ArcadeStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.ARCADE
        super().__init__(data)


class ArenaStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.ARENA
        super().__init__(data)


class UHCStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.UHC
        super().__init__(data)


class MCGOStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.MCGO
        super().__init__(data)


class BattlegroundStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.BATTLEGROUND
        super().__init__(data)


class SuperSmashStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.SUPER_SMASH
        super().__init__(data)


class GingerBreadStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.GINGERBREAD
        super().__init__(data)


class HousingStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.HOUSING
        super().__init__(data)


class SkyWarsStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.SKYWARS
        super().__init__(data)


class TrueCombatStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.TRUE_COMBAT
        super().__init__(data)


class SpeedUHCStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.SPEED_UHC
        super().__init__(data)


class SkyClashStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.SKYCLASH
        super().__init__(data)


class LegacyStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.LEGACY
        super().__init__(data)


class PrototypeStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.PROTOTYPE
        super().__init__(data)


class BedwarsStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.BEDWARS
        super().__init__(data)

    def level(self) -> float:
        """
        Calculate the player's Bedwars level

        Returns
        -------
        float:
            The player's Bedwars level
        """
        exp_per_prestige = 489000
        levels_per_prestige = 100

        exp = getattr(self, "Experience", 0.0)
        prestige = int(exp/exp_per_prestige)
        exp = exp % exp_per_prestige

        if prestige > 5:
            over = prestige % 5
            exp += over * exp_per_prestige
            prestige -= over

        if exp < 500:
            return 0 + prestige * levels_per_prestige
        elif exp < 1500:
            return 1 + prestige * levels_per_prestige
        elif exp < 3500:
            return 2 + prestige * levels_per_prestige
        elif exp < 5500:
            return 3 + prestige * levels_per_prestige
        elif exp < 9000:
            return 4 + prestige * levels_per_prestige

        exp -= 9000
        return (exp / 5000 + 4) + (prestige * levels_per_prestige)


class MurderMysteryStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.MURDER_MYSTERY
        super().__init__(data)


class BuildBattleStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.BUILD_BATTLE
        super().__init__(data)


class DuelsStats(PlayerStats):
    def __init__(self, data: dict):
        self.game = GameType.DUELS
        super().__init__(data)
