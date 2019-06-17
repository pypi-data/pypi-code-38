import logging
from .base import MUDObject
from .base import MUDInterface

class ChannelInterface(MUDInterface):

    name = 'channel'
    channels = {}

    def load_channels(self):
        channels = {}
        for k, channel_class in self.channels.items():
            channels[k] = channel_class()
        return channels

    def add_player_to_valid_channels(self, player):
        for channel in self.engine.channels.values():
            channel.add_player(player)

    def add_player_to_channel(self, player, channel_name):

        channel = self.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.add_player(player)

    def remove_player_from_channel(self, player, channel_name):

        channel = self.get_channel_by_name(channel_name)

        if not channel:
            logging.warning("Channel {} not listed in the MUD".format(channel_name))
            return

        channel.remove_player(player)

    def get_channel_by_name(self, channel_name):
        return self.engine.channels.get(channel_name, None)

class MetaChannel(type):

    channel = None

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        if inst.name:
            MUDInterface.get_interface("channel").channels[inst.name] = inst
        return inst

class Channel(MUDObject, metaclass=MetaChannel):

    name = None
    _INSTANCE = None

    def __init__(self):

        if self._INSTANCE:
            return self._INSTANCE

        self.players = []
        self.interface = MUDInterface.get_interface("channel")()

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        if self in player.channels:
            player.channels.remove(self)

    def add_player(self, player, validate=True):
        if player in self.players:
            logging.debug("Player {} is already in channel {}".format(player.name, self.name))

        elif validate and self.can_join(player):
            self.players.append(player)
            player.channels.append(self)
        else:
            logging.debug("Unable to add player {} to channel {}".format(player, self))

    def send_message(self, msg, prompt=True):
        for player in self.players:
            player.queue_message(msg + "\r\n", prompt=prompt)

    def can_join(self, player):
        return True

class GeneralChannel(Channel):

    name = 'general'

class AdminChannel(Channel):

    name = 'admin'

    def can_join(self, player):
        return True if player.admin else False
