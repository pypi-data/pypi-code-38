from datetime import datetime

from ..utils import get_player_name


class Friend:

    def __init__(self, _id: str, sender_uuid: str,
                 receiver_uuid: str, started: int):
        self._id = _id
        self.sender_uuid = sender_uuid
        self.receiver_uuid = receiver_uuid
        self.started = datetime.utcfromtimestamp(started / 1000)

    def __repr__(self):
        return "<Friend _id={0._id} sender_uuid={0.sender_uuid} " \
               "receiver_uuid={0.receiver_uuid}>".format(self)

    async def sender_name(self):
        """
        Get the username of the player who sent the friend request
        """
        return await get_player_name(self.sender_uuid)

    async def receiver_name(self):
        """
        Get the username of the player who received the friend request
        """
        return await get_player_name(self.receiver_uuid)
