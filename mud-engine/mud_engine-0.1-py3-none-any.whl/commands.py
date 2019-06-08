import logging
from .base import MUDObject
from .base import MUDInterface

class CommandInterface(MUDInterface):
    name = 'command'
    commands = {}

class MetaCommand(type):

    command = None

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        if inst.command:
            CommandInterface.commands[inst.command] = inst
        return inst

class Command(MUDObject, metaclass=MetaCommand):

    interface = CommandInterface

    def __init__(self, player, args=None):
        self.player = player
        self.args = args or []

    def execute(self):
            logging.debug("Running command {}".format(self))

class QuitCommand(Command):

    command = 'quit'

    def execute(self):
        self.player.disconnect()

class ShutdownCommand(Command):

    command = 'shutdown'

    def execute(self):
        self.interface.engine.shutdown = True

class EchoCommand(Command):

    command = 'echo'

    def execute(self):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self.player, self.args + "\r\n"))

class TellCommand(Command):

    command = 'tell'

    def execute(self):

        from .events import PlayerMessageEvent
        from .events import TellEvent

        recip_name, msg = self.args.split(None, 1)

        recip = self.interface.engine.get_player_by_name(recip_name)

        if not recip:
            self.interface.event.emit_event(PlayerMessageEvent(self.player, "Unknown player {}\r\n".format(recip_name)))
        else:
            self.interface.event.emit_event(TellEvent(self.player, recip, msg))
