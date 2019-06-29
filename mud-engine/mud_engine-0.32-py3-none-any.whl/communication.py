import logging
from .base import MUDObject
from .base import MUDInterface

# engine -> message_bus -> server -> client

# engine <-> ??? <-> socket <-> telnetclient

# engine <-> MQ <-> http <-> httpclient

class MetaMessageColor(type):

    _colors = {}

    def __str__(cls):
        return cls.color_code or ""

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        if name != 'MessageColor':
            cls._colors[name.lower()] = inst
            if not inst.color_code:
                inst.color_code = f"%%{name.upper()}%%"
        return inst

class MessageColor(object, metaclass=MetaMessageColor):

    color_code = None

class NoColor(MessageColor):
    pass

class Blue(MessageColor):
    pass

class Brown(MessageColor):
    pass

class Cyan(MessageColor):
    pass

class Green(MessageColor):
    pass

class Grey(MessageColor):
    pass

class LightBlue(MessageColor):
    pass

class LightCyan(MessageColor):
    pass

class LightGreen(MessageColor):
    pass

class LightRed(MessageColor):
    pass

class Magenta(MessageColor):
    pass

class Pink(MessageColor):
    pass

class Red(MessageColor):
    pass

class White(MessageColor):
    pass

class Yellow(MessageColor):
    pass


class MUDMessage(object):

    _colors = MetaMessageColor._colors

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        message = self.message
        for color in MetaMessageColor._colors.values():
            message = message.replace(color.color_code, "")
        return message

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
    _instance = None

    def __init__(self):
        super().__init__()

        if self._instance:
            return self._instance

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
            logging.debug(f"Adding player to {self} channel for comm")
            if player not in self.players:
                self.players.append(player)
            if self not in player.channels:
                player.channels.append(self)
        else:
            logging.debug("Unable to add player {} to channel {}".format(player, self))

    def queue_message(self, msg, auto_format=True, prompt=True):
        for player in self.players:
            player.queue_message(msg, auto_format=auto_format, prompt=prompt)

    def can_join(self, player):
        return True

class GeneralChannel(Channel):

    name = 'general'

class AdminChannel(Channel):

    name = 'admin'

    def can_join(self, player):
        return True if player.admin else False
