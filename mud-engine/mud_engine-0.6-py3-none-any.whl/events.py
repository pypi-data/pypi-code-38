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
        self.interface = MUDInterface.get_interface("event")()

    def execute(self):
        logging.info("Running event {}".format(self))

class ConnectionEvent(Event):

    name = 'connect'

    def __init__(self, client):
        super().__init__()
        self.client = client

    def execute(self):
        self.interface.event.emit_event(LoginEvent(self.client.player))

class DisconnectEvent(Event):

    name = 'disconnect'

    def __init__(self, client):
        super().__init__()
        self.client = client

class LoginEvent(Event):

    """ Init login - happens when a player is connected and is logging in
    """
    name = 'login'

    def __init__(self, player):
        super().__init__()
        self.player = player

    def execute(self):

        from .player import Player

        if self.player.state == self.player.STATE_CONNECTING:
            self.player.send_message("Login:", prompt=False)

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
    def __init__(self, player, msg, prompt=True):
        super().__init__()
        self.player = player
        self.msg = msg
        self.prompt = prompt

    def execute(self):
        self.player.send_message("{}".format(self.msg), self.prompt)

class TellEvent(MessageEvent):
    """ Event to send a message to a player from a player
    """

    def __init__(self, player, recip, msg):
        super().__init__()
        self.player = player
        self.recip = recip
        self.msg = msg

    def execute(self):
        self.player.send_line("You tell {}, {}".format(self.recip.name, self.msg))
        self.recip.send_line("{} tells you {}".format(self.player.name, self.msg))
