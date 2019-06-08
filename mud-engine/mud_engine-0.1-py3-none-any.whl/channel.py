import logging
from .base import MUDObject
from .base import MUDInterface

class ChannelInterface(MUDInterface):

    name = 'channel'

    @classmethod
    def add_player_to_channel(cls, player, channel_name):

        channel = cls.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.players.append(player)
        player.channels.append(channel)

    @classmethod
    def remove_player_from_channel(cls, player, channel_name):

        channel = cls.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.players.remove(player)
        player.channels.remove(channel)

    @classmethod
    def get_channel_by_name(cls, channel_name):
        return cls.engine.channels.get(channel_name, None)

class Channel(MUDObject):

    interface = ChannelInterface

    def __init__(self, name):

        self.name = name
        self.players = []
