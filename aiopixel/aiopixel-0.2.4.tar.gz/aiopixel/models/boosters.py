from datetime import datetime

from aiopixel import GameType
from ..utils import get_player_name


class Booster:
    """
    A booster
    """

    def __init__(self, _id: str, purchaser_uuid: str, amount: float,
                 original_length: int, length: int, game_type: int,
                 activated_at: int, stacked: list=None):
        self._id = id
        self.purchaser_uuid = purchaser_uuid
        self.amount = amount
        self.original_length = original_length
        self.length = length
        self.game_type = GameType.from_id(game_type)
        self.activated_at = datetime.utcfromtimestamp(activated_at / 1000)
        self.stacked = stacked

    def __repr__(self):
        return "<Booster id={0._id} purchaser={0.purchaser} " \
               "length={0.length} game_type={0.game_type.id}>".format(self)

    async def purchaser_name(self):
        """
        Get the purchaser's name
        """
        return await get_player_name(self.purchaser_uuid)
