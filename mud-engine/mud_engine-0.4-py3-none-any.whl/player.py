import logging
from .base import MUDObject
from .base import MUDInterface

class PlayerInterface(MUDInterface):

    name = 'player'

    def get_player_by_name(self, name):
        for player in self.engine.players:
            if player.name == name:
                return player
        return None

class Player(MUDObject):

    state = None
    name = None
    location = None
    level = 0
    hit_points = 0
    mana_points = 0
    move_points = 0
    max_hit_points = 100
    max_mana_points = 100
    max_move_points = 100

    def __init__(self):
        self.interface = MUDInterface.get_interface("player")()
        self.hit_points = self.max_hit_points
        self.mana_points = self.max_mana_points
        self.move_points = self.max_move_points
        self.classes = []
        self.inventory = []
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

    def set_location(self, new_location):

        new_location.players.append(self)
        if self.location:
            self.location.players.remove(self)
        self.location = new_location

    def move(self, direction):

        new_location = getattr(self.location, direction)
        if not new_location:
            self.queue_message("You can't move in that direction\r\n")
            return

        self.set_location(new_location)
        self.location.render_to_player(self)
        entrance_descriptions = {
            "up": "from below",
            "south": "from the north",
            "east":"from the west",
            "down": "from above",
            "north": "from the south",
            "west":"from the east",
        }
        for player in new_location.players:
            if self != player:
                player.queue_message("\r\n{} enters in from the {}\r\n".format(self.name, entrance_descriptions[direction]))

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
            self.send_message("", prompt=True)
            return

        command_cls = self.interface.command.commands.get(cmd)
        command = None if not command_cls else command_cls(self, args)

        if not command_cls or not command.can_do():
            self.send_line("Unknown command {}".format(cmd))
            return

        command.execute()

    def disconnect(self):
        self.location.players.remove(self)
        for channel in self.channels:
            channel.players.remove(self)
        self.interface.engine.disconnect_player(self)
        del self