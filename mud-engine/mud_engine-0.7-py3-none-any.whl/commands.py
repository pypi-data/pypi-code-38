import logging
from .base import MUDObject
from .base import MUDInterface
from .base import StopAction
import inspect

class CommandInterface(MUDInterface):

    name = 'command'

    def command_lookup(self, cmd):
        cmd = cmd.lower()
        for command, command_cls in sorted(MetaCommand._KNOWN_COMMANDS.items(), key=lambda x: f"{x[1].sort_order*-1}_{x[0]}"):
            if not command_cls.full_match and command.startswith(cmd):
                return command_cls
            elif command == cmd:
                return command_cls
        return None

class MetaCommand(type):

    _KNOWN_COMMANDS = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        cmd = inst.command or name
        if cmd and cmd not in ("MetaCommand", "Command"):
            cls._KNOWN_COMMANDS[cmd.lower()] = inst
        return inst

class Command(MUDObject, metaclass=MetaCommand):

    command = None
    sort_order = 0 # Force the command to be sorted up on command lookup, higher values match first
    full_match = False # Whether commands have be typed fully

    def __init__(self, player, args=None):
        super().__init__()
        self.player = player
        self.args = args or []
        self.interface = MUDInterface.get_interface("command")()

    def can_do(self):
        return True

    def do(self):
        logging.debug("Running command {}".format(self))

class Unknown(Command):
    """ Unknown is a special command, it will be called for all unknown commands"""
    def do(self):
        self.player.queue_message("Unknown command {}\r\n".format(self.args))

class Quit(Command):

    def do(self):
        self.player.disconnect()


class Echo(Command):

    def do(self):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self.player, (self.args or "") + "\r\n"))

class Tell(Command):

    def do(self):

        from .events import PlayerMessageEvent
        from .events import TellEvent

        recip_name, msg = self.args.split(None, 1)

        recip = self.interface.player.get_player_by_name(recip_name)

        if not recip:
            self.interface.event.emit_event(PlayerMessageEvent(self.player, "Unknown player {}\r\n".format(recip_name)))
        else:
            self.interface.event.emit_event(TellEvent(self.player, recip, msg))

class Chat(Command):

    def do(self):
        msg = "# general - {}:{}".format(self.player.name, self.args)
        self.interface.channel.get_channel_by_name("general").send_message(msg)

class Look(Command):

    def do(self):
        self.player.location.render_to_player(self.player)

class Who(Command):

    def do(self):
        msg = "Connected players:\r\n"
        msg += "\r\n".join([v.name for v in self.interface.engine.players])
        msg += "\r\n"
        self.player.queue_message(msg)

def MagicSpell(cls, mana_cost=100):

    orig_can_do = cls.can_do

    def can_do(self):
        if self.player.mana_points < mana_cost:
            self.player.queue_message("You don't have enough mana points!\r\n")
            raise StopAction()
        return orig_can_do(self)

    orig_do = cls.do

    def do(self):
        self.player.mana_points -= mana_cost
        return orig_do(self)

    cls.can_do = can_do
    cls.do = do
    return cls

class CommandDecorator(object):

    def __init__(self, *args, **kwargs):
        if args and inspect.isclass(args[0]):
            self.cls = args[0]
            self.args = []
            self.kwargs = kwargs
            self.decorate()
        else:
            self.args = args
            self.kwargs = kwargs

    def __call__(self, cls):
        self.cls = cls
        self.decorate()

    def decorate(dself):
        pass

class Living(CommandDecorator):

    def decorate(dself):

        cls = dself.cls
        orig_can_do = cls.can_do

        def can_do(self):
            if not orig_can_do(self):
                return True
            if self.player.in_state("dead"):
                self.player.queue_message("You're dead!\r\n")
                raise StopAction()
            return True

        cls.can_do = can_do
        return cls

class Movement(Living):

    def decorate(self):
        super().decorate()

        move_point_cost = self.args[0] if self.args else None
        if move_point_cost is None:
            move_point_cost = self.kwargs.get("move_point_cost", 10)

        cls = self.cls
        orig_can_do = cls.can_do

        def can_do(self):
            if not orig_can_do(self):
                return False # Check parent first, which is if it's living
            if self.player.move_points - move_point_cost < 0:
                self.player.queue_message("You don't have enough move points!\r\n")
                raise StopAction()
            return True

        orig_do = cls.do

        def do(self):
            orig_do(self)
            self.player.move_points -= move_point_cost

        cls.can_do = can_do
        cls.do = do
        return cls

class AdminCommand(CommandDecorator):

    def decorate(dself):

        orig_can_do = dself.cls.can_do

        def can_do(self):
            if not orig_can_do(self):
                return False
            return True if self.player.admin else False

        dself.cls.can_do = can_do
        return dself.cls

class MagicSpell(Living):

    def decorate(self):
        super().decorate()

        mana_point_cost = self.args[0] if self.args else None
        if mana_point_cost is None:
            mana_point_cost = self.kwargs.get("mana_point_cost", 10)

        cls = self.cls
        orig_can_do = cls.can_do

        def can_do(self):
            orig_can_do(self) # Check parent first, which is if it's living
            if self.player.mana_points - mana_point_cost < 0:
                self.player.queue_message("You don't have enough mana points!\r\n")
                raise StopAction()

        orig_do = cls.do

        def do(self):
            orig_do(self)
            self.player.mana_points -= mana_point_cost

        cls.can_do = can_do
        cls.do = do
        return cls

@Movement
class Down(Command):

    sort_order = 100

    def do(self):
        self.player.move('down')

@Movement
class Up(Command):

    sort_order = 100

    def do(self):
        self.player.move('up')

@Movement
class East(Command):

    sort_order = 100

    def do(self):
        self.player.move('east')

@Movement
class West(Command):

    sort_order = 100

    def do(self):
        self.player.move('west')

@Movement
class South(Command):

    sort_order = 100

    def do(self):
        self.player.move('south')

@Movement
class North(Command):

    sort_order = 100

    def do(self):
        self.player.move('north')

@MagicSpell
class Float(Command):

    def can_do(self):
        if self.player.in_state("floating"):
            self.player.queue_message("You are already floating!\r\n")
            raise StopAction()
        return True

    def do(self):

        from .player import Floating
        self.player.add_state(Floating)
        self.player.queue_message("You gently float into the air\r\n")

### Admin commands

@AdminCommand
class Shutdown(Command):

    full_match = True

    def do(self):
        self.interface.engine.shutdown = 1

@AdminCommand
class GoTo(Command):

    def can_do(self):

        if not self.args:
            self.player.queue_message("To whom would you like to goto?\r\n")
            raise StopAction()

    def do(self):

        other_player = self.interface.player.get_player_by_name(self.args)
        if not other_player:
            self.player.queue_message("To whom would you like to goto?\r\n")
            return

        self.player.set_location(other_player.location)
        self.player.queue_message(f"You open a portal and jump through, landing before {other_player.name}!\r\n")
        other_player.queue_message(f"\r\nA portal appears and {self.player.name} jumps out!\r\n")

