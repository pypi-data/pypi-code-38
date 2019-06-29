import logging
from .base import MUDObject
from .base import MUDInterface
from .base import StopAction
from .base import MUDDecorator
from .base import MUDMessage
from .help import Help as MUDHelp

class CommandInterface(MUDInterface):

    name = 'command'

    def command_lookup(self, cmd):
        cmd = cmd.lower()
        for command, command_cls in sorted(MetaCommand._known_commands.items(), key=lambda x: f"{x[1].sort_order*-1}_{x[0]}"):
            if not command_cls.full_match and command.startswith(cmd):
                return command_cls
            elif command == cmd:
                return command_cls
        return None

class MetaCommand(type):

    _known_commands = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        cmd = inst._command or name
        cmd = cmd.lower()
        if cmd and cmd not in ("MetaCommand", "Command"):
            cls._known_commands[cmd.lower()] = inst

        if inst.help and not isinstance(inst.help, MUDHelp):
            inst.help = MUDHelp(cmd, inst.help)

        inst.command = cmd

        return inst

class Command(MUDObject, metaclass=MetaCommand):

    _command = None
    help = None
    sort_order = 0 # Force the command to be sorted up on command lookup, higher values match first
    full_match = False # Whether commands have be typed fully

    def __init__(self, player, args=None, raw_line=None):
        super().__init__()
        self.player = player
        self.args = args or []
        self.raw_line = raw_line
        self.interface = MUDInterface.get_interface("command")()

    def can_do(self):
        return True

    def do(self):
        logging.debug("Running command {}".format(self))

class Unknown(Command):
    """ Unknown is a special command, it will be called for all unknown commands"""
    def do(self):
        self.player.queue_message(f"Unknown command {self.raw_line}")

class Living(MUDDecorator):

    def decorate(dself):

        cls = dself.cls
        orig_can_do = cls.can_do

        def can_do(self):
            if not orig_can_do(self):
                return True
            if self.player.in_state("dead"):
                self.player.queue_message("You're dead!")
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
                self.player.queue_message("You don't have enough move points!")
                raise StopAction()
            return True

        orig_do = cls.do

        def do(self):
            orig_do(self)
            self.player.move_points -= move_point_cost

        cls.can_do = can_do
        cls.do = do
        return NavigationCommand(cls)

class NavigationCommand(MUDDecorator):

    def decorate(dself):

        if dself.cls.help:
            dself.cls.help.set_classification("navigation")

        return dself.cls

class CommunicationCommand(MUDDecorator):

    def decorate(dself):

        if dself.cls.help:
            dself.cls.help.set_classification("communication")

        return dself.cls

class AdminCommand(MUDDecorator):

    def decorate(dself):

        if dself.cls.help:
            dself.cls.help.set_classification("admin")

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

        if self.cls.help:
            self.cls.help.set_classification("spell")

        mana_point_cost = self.args[0] if self.args else None
        if mana_point_cost is None:
            mana_point_cost = self.kwargs.get("mana_point_cost", 10)

        cls = self.cls
        orig_can_do = cls.can_do
        cls.mana_point_cost = mana_point_cost

        def can_do(self):
            orig_can_do(self) # Check parent first, which is if it's living
            if self.player.mana_points - mana_point_cost < 0:
                self.player.queue_message("You don't have enough mana points!")
                raise StopAction()
            return True

        orig_do = cls.do

        def do(self):
            orig_do(self)
            self.player.mana_points -= mana_point_cost

        cls.can_do = can_do
        cls.do = do
        return cls

class Quit(Command):

    def do(self):
        self.player.disconnect()

class Help(Command):

    def do(self):

        if not self.args:
            self.player.queue_message(self.interface.help.default_help())
            return;

        help = self.interface.help.help_lookup(self.args[0])
        if not help:
            self.player.queue_message(f"{self.args[0]} isn't a known help topic")
            return
        self.player.queue_message(f"{help.details}")

class Echo(Command):

    help = """syntax: echo <args>

Simply echoes whatever arguments are given to it back to the player"""

    def do(self):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self.player, (self.args or "")))

@CommunicationCommand
class Tell(Command):

    help = """syntax: tell <player> <message>
    
Send a player a private message"""

    def do(self):

        recip_name, msg = self.args[0], " ".join(self.args[1:])

        # Try to find the person in this location first
        recip = self.interface.player.get_player_by_partial(recip_name, location=self.player.location, include_npcs=True)
        if not recip:
            recip = self.interface.player.get_player_by_partial(recip_name)

        if not recip:
            self.player.queue_message(f"Unknown player {recip_name}")
        else:
            self.player.queue_message(f"You tell {recip.name}, {msg}")
            recip.queue_message(MUDMessage(f"{self.player.name} tells you, {msg}",
                context={"player": self.player, "command": "tell"}))

@CommunicationCommand
class Say(Command):

    help = """syntax: say <msg> 
    
Tell players at your location a message"""

    def do(self):

        msg = self.raw_line[4:]
        self.player.message_location(
            f"You say {msg}",
            other_player_message = MUDMessage(
                f"{self.player.name} says, {msg}",
                context={"player": self.player, "command": "say"}
            )
        )

@CommunicationCommand
class Chat(Command):

    help = """syntax: chat <msg> 
    
Sends the general chat channel a message"""

    def do(self):

        msg = "# general - {}:{}".format(self.player.name, " ".join(self.args))
        self.interface.channel.get_channel_by_name("general").queue_message(msg)

@NavigationCommand
class Look(Command):

    help = """syntax: look [direction] 
    
Look in a room or in a direction"""

    def do(self):

        if not self.args:
            self.player.location.render_to_player(self.player)
            return

        first_arg = self.args[0].lower()

        first_arg = "north" if first_arg == "n" else first_arg
        first_arg = "south" if first_arg == "s" else first_arg
        first_arg = "east" if first_arg == "e" else first_arg
        first_arg = "west" if first_arg == "w" else first_arg
        first_arg = "up" if first_arg == "u" else first_arg
        first_arg = "down" if first_arg == "d" else first_arg

        if first_arg in ("north", "south", "east", "west", "up", "down"):

            direction = first_arg

            geo = getattr(self.player.location, direction)

            if not geo:
                dir_desc = "There's nothing to see in that direction"
            else:
                dir_desc = geo.entrance_descriptions.get(direction)
                if not dir_desc:
                    dir_desc = geo.entrance_descriptions.get("default") or "There's nothing to see in that direction"

            self.player.queue_message(dir_desc)
        else:
            self.player.queue_message("Who/what/where do you want to at or in?")

@CommunicationCommand
class Who(Command):

    help = """syntax: who 
    
List connected players"""

    def do(self):
        msg = "Connected players:\r\n"
        msg += "\r\n".join([v.name for v in self.interface.engine.players])
        self.player.queue_message(msg)

@Movement
class Down(Command):

    help = """syntax: down
    
Move your player down. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('down')

@Movement
class Up(Command):

    help = """syntax: up
    
Move your player up. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('up')

@Movement
class East(Command):

    help = """syntax: east
    
Move your player east. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('east')

@Movement
class West(Command):

    help = """syntax: west
    
Move your player west. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('west')

@Movement
class South(Command):

    help = """syntax: south
    
Move your player south. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('south')

@Movement
class North(Command):

    help = """syntax: north
    
Move your player north. Costs a small amount of move points"""

    sort_order = 100

    def do(self):
        self.player.move('north')

@MagicSpell
class Float(Command):

    def can_do(self):
        if self.player.in_state("floating"):
            self.player.queue_message("You are already floating!")
            raise StopAction()
        return True

    def do(self):

        from .player import Floating
        self.player.add_state(Floating)
        self.player.queue_message("You gently float into the air")

### Admin commands

@AdminCommand
class Shutdown(Command):

    full_match = True

    def do(self):
        count_down = 5
        if self.args and self.args[0]:
            count_down = int(self.args[0])
        self.interface.engine.shutdown = count_down

@AdminCommand
class GoTo(Command):

    def can_do(self):

        if not self.args:
            self.player.queue_message("To whom would you like to goto?")
            raise StopAction()

        return True

    def do(self):

        other_player = self.interface.player.get_player_by_partial(self.args[0])
        if not other_player:
            self.player.queue_message("To whom would you like to goto?")
            return

        if other_player == self.player:
            self.player.queue_message("You can't go to yourself!")

        self.player.set_location(other_player.location)
        self.player.message_location(
            f"You open a portal and jump through, landing before {other_player.name}!",
            f"A portal appears and {self.player.name} jumps out!"
        )

class Kill(Command):

    def do(self):

        victim = None
        if self.args and self.args[0]:
            for other_player in self.player.location.players:
                if other_player.name.lower().startswith(self.args[0].lower()):
                    victim = other_player
                    break

        if not victim:
            self.player.queue_message("Who do you want to kill?")
            return

        self.player.message_location(
            f"You lash out and kill {other_player.name}",
            f"{self.player.name} lashes out and kills {other_player.name}!",
            unique_messages = {
                victim: f"{self.player.name} lashes out and kills you!"
            }
        )


