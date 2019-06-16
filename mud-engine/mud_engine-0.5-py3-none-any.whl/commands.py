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
            MUDInterface.get_interface("command").commands[inst.command] = inst
        return inst

class Command(MUDObject, metaclass=MetaCommand):

    def __init__(self, player, args=None):
        self.player = player
        self.args = args or []
        self.interface = MUDInterface.get_interface("command")()

    def can_do(self):
        return True

    def execute(self):
        logging.debug("Running command {}".format(self))

class QuitCommand(Command):

    command = 'quit'

    def execute(self):
        self.player.disconnect()


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

        recip = self.interface.player.get_player_by_name(recip_name)

        if not recip:
            self.interface.event.emit_event(PlayerMessageEvent(self.player, "Unknown player {}\r\n".format(recip_name)))
        else:
            self.interface.event.emit_event(TellEvent(self.player, recip, msg))

class ChatCommand(Command):

    command = 'chat'

    def execute(self):
        msg = "# general - {}:{}".format(self.player.name, self.args)
        self.interface.channel.get_channel_by_name("general").send_message(msg)

class LookCommand(Command):

    command = 'look'

    def execute(self):
        self.player.location.render_to_player(self.player)

class WhoCommand(Command):

    command = 'who'

    def execute(self):
        msg = "Connected players:\r\n"
        msg += "\r\n".join([v.name for v in self.interface.engine.players])
        msg += "\r\n"
        self.player.queue_message(msg)

class DownCommand(Command):

    command = 'down'
    sort_order = 100

    def execute(self):
        self.player.move('down')

class UpCommand(Command):

    command = 'up'
    sort_order = 100

    def execute(self):
        self.player.move('up')

class EastCommand(Command):

    command = 'east'
    sort_order = 100

    def execute(self):
        self.player.move('east')

class WestCommand(Command):

    command = 'west'
    sort_order = 100

    def execute(self):
        self.player.move('west')

class SouthCommand(Command):

    command = 'south'
    sort_order = 100

    def execute(self):
        self.player.move('south')

class NorthCommand(Command):

    command = 'north'
    sort_order = 100

    def execute(self):
        self.player.move('north')

### Admin commands

class AdminCommand(Command):

    def can_do(self):
        return True if self.player.admin else False

class ShutdownCommand(AdminCommand):

    command = 'shutdown'

    def execute(self):
        self.interface.engine.shutdown = 1
