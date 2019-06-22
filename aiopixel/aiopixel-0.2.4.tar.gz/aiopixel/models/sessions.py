from ..gametypes import GameType


class PlayerSession:
    def __init__(self, data: dict):
        self.game_type = getattr(GameType, data["gameType"])
        self.server = data["server"]
        self.players = data["players"]
