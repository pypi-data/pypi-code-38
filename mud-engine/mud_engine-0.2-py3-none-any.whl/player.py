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
    hit_points = 0
    mana_points = 0
    move_points = 0
    max_hit_points = 0
    max_mana_points = 0
    max_move_points = 0

    def __init__(self):
        self.interface = PlayerInterface()
        self.hit_points = self.max_hit_points
        self.mana_points = self.max_mana_points
        self.move_points = self.max_move_points

    def change_location(self, new_location):
        new_location.players.append(self)
        if self.location:
            self.location.players.remove(self)
        self.location = new_location

    def move(self, direction):
        new_location = getattr(self.location, direction)
        if not new_location:
            self.queue_message("You can't move in that direction\r\n")
            return

        self.change_location(new_location)
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

class HumanPlayer(Player):

    STATE_CONNECTING = 1
    STATE_USERNAME = 2
    STATE_CONNECTED = 3
    prompt = "> "
    prompt_enabled = True

    def __str__(self):
        if self.name:
            return "ConnectedPlayer <{}>".format(self.name)
        return "ConnectingPlayer <{}>".format(self.client.address)

    def __init__(self, client):
        super().__init__()
        self.channels = []
        self.client = client
        self.state = self.STATE_CONNECTING

    def queue_message(self, message, prompt = True):
        from .events import PlayerMessageEvent
        self.interface.event.emit_event(PlayerMessageEvent(self, message, prompt))

    def send_message(self, message, prompt=True):
        self.client.send_message(message + (self.prompt if self.prompt_enabled and prompt else ""))

    def send_line(self, message, prompt=True):
        if message and not message.endswith("\r\n"):
            message += "\r\n"
        self.send_message(message, prompt=prompt)

    def handle_login(self, input):

        from .events import LoginEvent

        if self.state == self.STATE_CONNECTING: # First message after initial connection
            self.name = input
            self.state = self.STATE_CONNECTED
            self.interface.event.emit_event(LoginEvent(self))
            self.interface.engine.connect_player(self)
            self.send_line("Welcome, {}".format(self.name), prompt=False)

            self.interface.channel.add_player_to_channel(self, "general")

    def handle_command(self, input):

        if self.state != self.STATE_CONNECTED:
            return self.handle_login(input)

        command, args = "", ""

        if input:
            v = input.split(None, 1)
            command, args = v[0], v[1] if len(v) > 1 else ""

        if command == "":
            self.send_message("", prompt=True)
        elif not command in self.interface.command.commands:
            self.send_line("Unknown command {}".format(command))
        else:
            self.interface.command.commands[command](self, args).execute()

    def disconnect(self):
        self.location.players.remove(self)
        for channel in self.channels:
            channel.players.remove(self)
        self.interface.engine.disconnect_player(self)
        del self