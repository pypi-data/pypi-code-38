import logging
import re
from .base import MUDObject
from .base import MUDInterface
from .base import StopAction
from .base import MUDMessage

class PlayerInterface(MUDInterface):

    name = 'player'

    def get_player_by_name(self, name, include_npcs=False, location=None):

        from .npc import NPC

        for player in self.engine.players:
            if not include_npcs and isinstance(player, NPC):
                continue
            if location and player.location != location:
                continue
            if player.name.lower() == name.lower():
                return player
        return None

    def get_player_by_partial(self, partial_name, include_npcs=False, location=None):

        from .npc import NPC

        for player in self.engine.players:
            if not include_npcs and isinstance(player, NPC):
                continue
            if location and player.location != location:
                return
            if player.name.lower().startswith(partial_name.lower()):
                return player
        return None

class PlayerStateMeta(type):

    _known_states = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        state = inst.name or name
        if state and state not in ("PlayerStateCommand", "PlayerState"):
            cls._known_states[state.lower()] = inst
            inst.name = state
        return inst
    pass

class PlayerState(MUDObject, metaclass=PlayerStateMeta):

    name = None
    heartbeats = 0
    duration = None

    def __init__(self, player=None):
        super().__init__()
        self.player = player
        self.activate()

    def activate(self):
        pass

    def heartbeat(self):

        if not self.player:
            return

        # If the player is dead, we don't need to do anything
        if self.player.in_state("dead"):
            return

        self.heartbeats += 1

        if self.duration and self.heartbeats > self.duration:
            self.deactivate()
            self.player.remove_state(self.name)
            del self
            import gc
            gc.collect()

    def deactivate(self):
        pass

class Dead(PlayerState):

    # Dead doesn't require a heartbeat
    heartbeat = None

    def activate(self):
        self.player.message_location("You are mortally wounded!",
                                        f"{self.player.name} has become mortally wounded")

    def deactivate(self):
        self.player.message_location("You've been revived!",
                                     f"{self.player.name} has been revived!")

class Standing(PlayerState):

    # Standing state doesn't require a heartbeat
    heartbeat = None

class Floating(PlayerState):
    pass

class Player(MUDObject):

    name = None
    location = None
    level = 0
    hit_points = 0
    mana_points = 0
    move_points = 0
    max_hit_points = 100
    max_mana_points = 100
    max_move_points = 100

    hit_regen_rate = 5
    mana_regen_rate = 5
    move_regen_rate = 5

    classes = []
    inventory = []
    states = {}

    client = None
    prompt = None
    prompt_enabled = True

    connected = True

    def __init__(self, *args, **kwargs):
        super().__init__()
        for k,v in kwargs.items():
            setattr(self, k, v)
        self.interface = MUDInterface.get_interface("player")()
        self.hit_points = self.max_hit_points
        self.mana_points = self.max_mana_points
        self.move_points = self.max_move_points
        self.equipment = {
            'head': None,
            'neck': None,
            'back': None,
            'chest': None,
            'shoulder': None,
            'main_hand': None,
            'off_hand': None,
            'arms': None,
            'hands': None,
            'waist': None,
            'legs': None,
            'feet': None,
            'main_finger': None,
            'off_finger': None
        }

    def queue_message(self, message, auto_format =True, prompt = True):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self, message, auto_format, prompt))

    def send_message(self, message, auto_format = True, prompt=True):
        if not message:
            message = "\r\n"
        elif auto_format:
            if not message.endswith("\r\n"):
                message += "\r\n"
            if not self.client.buff.endswith("\r\n") and not message.startswith("\r\n"):
                message = '\r\n' + message
        self.client.send_message(message + (self.prompt.render() if self.prompt_enabled and prompt else ""))

    def in_state(self, state_name):
        return True if state_name in self.states else False

    def get_state(self, state_name):
        return self.states.get(state_name, None)

    def is_class(self, klass):
        return True if klass in self.classes else False

    def add_state(self, state_cls):
        state = state_cls(self)
        self.states[state.name.lower()] = state

    def remove_state(self, state_name):
        state_name = state_name.lower()
        if state_name in self.states:
            state = self.states[state_name]
            state.player = None
            del self.states[state_name]

            state._deregister_heartbeat()

            del state

    def set_location(self, new_location):
        new_location.players.append(self)
        if self.location and self.location != new_location:
            self.location.players.remove(self)
        self.location = new_location

    def move(self, direction):
        self.location.move_player(self, direction)

    def die(self):
        self.add_state(Dead)

    def render_display_name(self):
        return self.name

    def heartbeat(self):

        # Has the player died?
        if self.hit_points <= 0:
            if not self.in_state("dead"):
                self.die()
            return

        if self.hit_points < self.max_hit_points:
            self.hit_points += self.hit_regen_rate
            if self.hit_points > self.max_hit_points:
                self.hit_points = self.max_hit_points
        if self.hit_points < 0:
            self.hit_points = 0

        if self.mana_points < self.max_mana_points:
            self.mana_points += self.mana_regen_rate
            if self.mana_points > self.max_mana_points:
                self.mana_points = self.max_mana_points
        if self.mana_points < 0:
            self.mana_points = 0

        if self.move_points < self.max_move_points:
            self.move_points += self.move_regen_rate
            if self.move_points > self.max_move_points:
                self.move_points = self.max_move_points
        if self.move_points < 0:
            self.move_points = 0

    def message_location(self, message=None, other_player_message=None, unique_messages=None):
        unique_messages = unique_messages or {}
        if message:
            self.queue_message(message)
        if other_player_message:
            for other_player in self.location.players:
                if other_player != self and other_player not in unique_messages:
                    other_player.queue_message(other_player_message)
        for other_player, msg in unique_messages.items():
            other_player.queue_message(msg)

    def handle_command(self, input):

        if not self.connected:
            return self.handle_login(input)

        cmd, args = "", ""

        if input:
            v = re.findall(r"('[^']+[^\/]'|\"[^\"]+\"|\S+)\s?", input)
            cmd, args = v[0], v[1:] if len(v) > 1 else ""

        if cmd == "":
            self.queue_message("", prompt=True)
            return

        logging.debug(f"Got cmd:{cmd} and args:{args} from {self}")

        command_cls = self.interface.command.command_lookup(cmd)
        command = None if not command_cls else command_cls(self, args, raw_line = input)

        try:
            if not command_cls or not command.can_do():
                unknown_command_cls = self.interface.command.command_lookup("unknown")
                unknown_command_cls(self, cmd, raw_line = input).do()
                return
        except StopAction:
            return

        command.do()

class PlayerPrompt(MUDObject):

    def __init__(self, player):
        self.player = player

    def render(self):

        from .communication import NoColor
        from .communication import LightCyan
        from .communication import Red
        from .communication import Yellow
        from .communication import LightGreen

        fmt_color = str(LightCyan)

        hp_str = f"{LightGreen}{self.player.hit_points}{fmt_color}"
        mp_str = f"{LightGreen}{self.player.mana_points}{fmt_color}"
        mv_str = f"{LightGreen}{self.player.move_points}{fmt_color}"

        hp_percent = self.player.hit_points / self.player.max_hit_points
        mp_percent = self.player.mana_points / self.player.max_mana_points
        mv_percent = self.player.move_points / self.player.max_move_points

        if hp_percent < .10:
            hp_str = f"{Red}{self.player.hit_points}{fmt_color}"
        elif hp_percent < .50:
            hp_str = f"{Yellow}{self.player.hit_points}{fmt_color}"

        if mp_percent < .10:
            mp_str = f"{Red}{self.player.mana_points}{fmt_color}"
        elif mp_percent < .50:
            mp_str = f"{Yellow}{self.player.mana_points}{fmt_color}"

        if mv_percent < .10:
            mv_str = f"{Red}{self.player.move_points}{fmt_color}"
        elif mv_percent < .50:
            mv_str = f"{Yellow}{self.player.move_points}{fmt_color}"

        return f"{fmt_color}<HP:{hp_str},MP:{mp_str},MV:{mv_str}>{NoColor} "

class ConnectingPlayer(Player):

    LOGIN_STATE_CONNECTING = 1
    LOGIN_STATE_USERNAME = 2
    LOGIN_STATE_AUTHENTICATE = 3
    LOGIN_STATE_CONNECTED = 4

    connected = False

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.login_state = self.LOGIN_STATE_CONNECTING
        self.name = None
        self.human_player = None

    def __str__(self):
        return "ConnectingPlayer <{}>".format(self.client)

    def handle_login(self, input=None):

        if self.login_state == self.LOGIN_STATE_CONNECTING: # First message after initial connection

            self.queue_message(f"Login:", auto_format=False, prompt=False)
            self.login_state = self.LOGIN_STATE_USERNAME

        elif self.login_state == self.LOGIN_STATE_USERNAME: # We've prompted for a login

            self.human_player = self.interface.player.get_player_by_name(input)
            if not self.human_player:
                self.human_player = HumanPlayer(name = input)
                self.queue_message(f"Welcoming {input}, we'll need to create you an account\r\n", auto_format=False, prompt=False)
            elif self.human_player.connected:
                self.human_player = None
                self.client.send_message("Player is already connected\r\n")
                self.disconnect()
                return

            self.queue_message(f"Password:", auto_format=False, prompt=False)
            self.login_state = self.LOGIN_STATE_AUTHENTICATE

        elif self.login_state == self.LOGIN_STATE_AUTHENTICATE:

            import hashlib

            player = self.human_player

            password = input

            if not player.password_hash:
                player.password_hash = hashlib.sha256(password.encode()).hexdigest()
            elif player.password_hash and player.password_hash != hashlib.sha256(password.encode()).hexdigest():
                self.human_player = None
                self.client.send_message("Invalid Password\r\n")
                self.disconnect()
                return

            player.client = self.client
            self.client.player = player
            self.interface.engine.connect_player(player)

            self.client = None
            del self

    def handle_command(self, input):
            return self.handle_login(input)

    def disconnect(self):
        self.interface.engine.disconnect_player(self)

class HumanPlayer(Player):

    connected = False
    password_hash = None

    def __str__(self):
        return "HumanPlayer <{}>".format(self.name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = []
        self.admin = False
        self.prompt = PlayerPrompt(self)

    def queue_message(self, message, auto_format =True, prompt = True):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self, message, auto_format, prompt))

    def disconnect(self):
        self.interface.engine.disconnect_player(self)
