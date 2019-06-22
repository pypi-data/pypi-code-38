from typing import List
from ..utils import get_player_name
from ..gametypes import GameType

__all__ = ["Leaderboard", "LeaderboardMember"]


class LeaderboardMember:
    def __init__(self, uuid: str):
        self.uuid = uuid

    async def name(self):
        """
        Get the username of a leaderboard member
        """
        return await get_player_name(self.uuid)


class Leaderboard:
    def __init__(self, path: str, prefix: str, count: int,
                 leaders: List[LeaderboardMember],
                 title: str, game_type: GameType):
        self.path = path
        self.prefix = prefix
        self.count = count
        self.leaders = leaders
        self.title = title
        self.game_type = game_type
