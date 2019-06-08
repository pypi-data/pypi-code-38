import logging
from .base import MUDObject
from .base import MUDInterface

class ChannelInterface(MUDInterface):

    name = 'channel'

    def add_player_to_channel(self, player, channel_name):

        channel = self.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.players.append(player)
        player.channels.append(channel)

    def remove_player_from_channel(self, player, channel_name):

        channel = self.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.players.remove(player)
        player.channels.remove(channel)

    def get_channel_by_name(self, channel_name):
        return self.engine.channels.get(channel_name, None)

class Channel(MUDObject):

    def __init__(self, name):

        self.name = name
        self.players = []
        self.interface = ChannelInterface()

    def send_message(self, msg, prompt=True):
        for player in self.players:
            player.queue_message(msg + "\r\n", prompt=prompt)
