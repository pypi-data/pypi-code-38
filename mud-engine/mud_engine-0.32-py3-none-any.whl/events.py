import logging
from .base import MUDObject
from .base import MUDInterface

class EventInterface(MUDInterface):
    name = 'event'

    def emit_event(self, evt):
        self.engine.events.append(evt)

class Event(MUDObject):

    name = ''

    def __init__(self):
        super().__init__()
        self.interface = MUDInterface.get_interface("event")()

    def execute(self):
        logging.info("Running event {}".format(self))

class DisconnectEvent(Event):

    name = 'disconnect'

    def __init__(self, client):
        super().__init__()
        self.client = client

class MessageEvent(Event):
    """ Base message event
    """
    pass

class IncomingMessageEvent(Event):
    """ Happens when a client sends a message to the server
    """

    def __init__(self, client, message):
        super().__init__()
        self.client = client
        self.message = message

class PlayerMessageEvent(MessageEvent):
    """ Event to send a message to a player
    """
    def __init__(self, player, msg, auto_format=True, prompt=True):
        super().__init__()
        self.player = player
        self.msg = msg
        self.auto_format = auto_format
        self.prompt = prompt

    def execute(self):
        self.player.send_message("{}".format(self.msg), auto_format = self.auto_format, prompt = self.prompt)
