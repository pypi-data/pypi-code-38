import logging
from .base import MUDObject
from .base import MUDInterface
from .base import StopAction

class PlayerInterface(MUDInterface):

    name = 'player'

    def get_player_by_name(self, name):
        for player in self.engine.players:
            if player.name.lower() == name.lower():
                return player
        return None

class PlayerStateMeta(type):

    _KNOWN_STATES = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        state = inst.name or name
        if state and state not in ("PlayerStateCommand", "PlayerState"):
            cls._KNOWN_STATES[state.lower()] = inst
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
        self.player.message_location("\r\nYou are mortally wounded!\r\n",
                                        f"\r\n{self.player.name} has become mortally wounded")

    def deactivate(self):
        self.player.message_location("\r\nYou've been revived!\r\n",
                                     f"\r\n{self.player.name} has been revived!")

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

    def __init__(self):
        super().__init__()
        self.interface = MUDInterface.get_interface("player")()
        self.hit_points = self.max_hit_points
        self.mana_points = self.max_mana_points
        self.move_points = self.max_move_points
        self.classes = []
        self.inventory = []
        self.states = {}
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
        if self.location:
            self.location.players.remove(self)
        self.location = new_location

    def move(self, direction):
        self.location.move_player(self, direction)

    def die(self):
        self.add_state(Dead)

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

class NPC(Player):
    pass

class PlayerPrompt(MUDObject):

    fmt_string = "<HP:{player.hit_points},MP:{player.mana_points},MV:{player.move_points}> "

    def __init__(self, player, fmt_string = None):
        self.player = player
        if fmt_string:
            self.fmt_string

    def render(self):
        return self.fmt_string.format(player = self.player)

class HumanPlayer(Player):

    STATE_CONNECTING = 1
    STATE_USERNAME = 2
    STATE_CONNECTED = 3
    STATE_DISCONNECTED = 4
    prompt = None
    prompt_enabled = True

    def __str__(self):
        if self.name:
            return "ConnectedPlayer <{}>".format(self.name)
        return "ConnectingPlayer <{}>".format(self.client.address)

    def __init__(self, client):
        super().__init__()
        self.channels = []
        self.client = client
        self.admin = False
        self.state = self.STATE_CONNECTING
        self.prompt = PlayerPrompt(self)

    def queue_message(self, message, prompt = True):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self, message, prompt))

    def send_message(self, message, prompt=True):
        self.client.send_message(message + (self.prompt.render() if self.prompt_enabled and prompt else ""))

    def send_line(self, message, prompt=True):
        if message and not message.endswith("\r\n"):
            message += "\r\n"
        self.send_message(message, prompt=prompt)

    def handle_login(self, input):

        from .events import LoginEvent

        if self.state == self.STATE_CONNECTING: # First message after initial connection
            self.name = input
            if self.name.lower() in self.interface.engine.admins:
                logging.info("Admin logging in {}".format(self.name))
                self.admin = True
            self.state = self.STATE_CONNECTED
            self.interface.event.emit_event(LoginEvent(self))
            self.interface.engine.connect_player(self)
            self.send_line("Welcome to {}, {}".format(self.interface.engine.name, self.name), prompt=False)

            self.interface.channel.add_player_to_valid_channels(self)

    def handle_command(self, input):

        if self.state != self.STATE_CONNECTED:
            return self.handle_login(input)

        cmd, args = "", ""

        if input:
            v = input.split(None, 1)
            cmd, args = v[0], v[1] if len(v) > 1 else ""

        if cmd == "":
            self.queue_message("", prompt=True)
            return

        command_cls = self.interface.command.command_lookup(cmd)
        command = None if not command_cls else command_cls(self, args)

        try:
            if not command_cls or not command.can_do():
                unknown_command_cls = self.interface.command.command_lookup("unknown")
                unknown_command_cls(self, cmd).do()
                return
        except StopAction:
            return

        command.do()

    def disconnect(self):
        self.state = HumanPlayer.STATE_DISCONNECTED
        self.location.players.remove(self)
        for channel in self.channels:
            channel.players.remove(self)
        self.interface.engine.disconnect_player(self)
        self._deregister_heartbeat()
        del self

    def message_location(self, message, other_player_message):
        self.queue_message(message)
        for other_player in self.location.players:
            if other_player != self:
                other_player.queue_message(other_player_message)
#
#class PlayerActionMeta(type):
#
#    _PLAYER_ACTIONS = {}
#
#    def __new__(cls, name, bases, dct):
#        inst = super().__new__(cls, name, bases, dct)
#        if name != 'PlayerAction':
#            cls._PLAYER_ACTIONS[name.lower()] = inst
#        return inst
#
#class PlayerAction(MUDObject, metaclass=PlayerActionMeta):
#    pass
#
#class Move(PlayerAction):
#
#    def do(self, player, direction):
#        if player.move_points:
#            super().move(direction)
#        else:
#            player.queue_message("You don't have enough move points!\r\n")
