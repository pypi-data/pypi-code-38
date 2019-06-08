import logging
from .base import MUDObject
from .base import MUDInterface

class PlayerInterface(MUDInterface):
    name = 'player'

    @classmethod
    def get_player_by_name(cls, name):
        for player in cls._INSTANCE.players:
            if player.name == name:
                return player
        return None

class Player(MUDObject):

    state = None
    name = None
    interface = PlayerInterface

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

    def send_message(self, message, prompt = True):
        self.client.send_message(message + (self.prompt if self.prompt_enabled and prompt else ""))

    def send_line(self, message):
        if message and not message.endswith("\r\n"):
            message += "\r\n"
        self.send_message(message, prompt=True)

    def handle_login(self, input):

        from .events import LoginEvent

        if self.state == self.STATE_CONNECTING: # First message after initial connection
            self.name = input
            self.state = self.STATE_CONNECTED
            self.interface.event.emit_event(LoginEvent(self))
            self.interface.engine.connect_player(self)
            self.send_line("Welcome, {}".format(self.name))

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
        self.interface.engine.disconnect_player(self)