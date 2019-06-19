import logging
from .base import MUDObject
from .base import MUDInterface
from .servers import MUDTCPSocket
from .base import _HEARTBEATS
from .base import StopAction
from .player import HumanPlayer
import time

class MUDEngine(MUDObject):

    pulse = 1.5 * 1000000000 # 1 beat per 1.5 seconds
    _LAST_HEARTBEAT = 0 # Nanoseconds since last heartbeat

    shutdown = 0
    name = "MUDEngine"

    def __init__(self, host="localhost", port=5000):
        self.port = port
        self.host = host
        self.socket = MUDTCPSocket()
        self.admins = [] # A list of names to make admins
        self.players = []
        self.events = []
        self.geography = []
        self.channels = {}
        self.interface = MUDInterface()
        MUDInterface.engine = self

        logging.info("Loading geography data")
        self.interface.geography.load_geography()

        logging.info("Loading communication channels")
        self.channels = self.interface.channel.load_channels()

    def run(self):

        logging.info("Running {} on {}:{}".format(self.name, self.host, self.port))
        self.socket.bind_and_listen(self.host, self.port)

        self._LAST_HEARTBEAT = time.time_ns()

        while True:

            t = time.time_ns()
            if t - self._LAST_HEARTBEAT > self.pulse:
                self.heartbeat()
                self._LAST_HEARTBEAT = t

            self.handle_events()
            self.socket.handle_incoming_connections()
            self.socket.handle_incoming_messages()

            if not self.shutdown:
                continue
            if self.shutdown == 3:
                logging.info("Shutdown command received, shutting down")
                return
            self.interface.channel.get_channel_by_name("general").send_message("Server shutting down in {}".format(self.shutdown), prompt=False)
            self.shutdown += 1



    def heartbeat(self):
        for obj, heartbeat in [(k,v) for k,v in _HEARTBEATS.items()]:
            if obj != self:
                heartbeat()

    def disconnect_player(self, player):

        logging.info("Disconnecting player {}".format(player))
        self.players.remove(player)
        self.socket.clients.remove(player.client)
        del player.client
        del player

    def connect_player(self, player):
        logging.info("Logging in player {}".format(player))
        self.players.append(player)
        player.set_location(self.geography[0])
        player.location.render_to_player(player)

    def handle_events(self):
        events = self.events
        self.events = []
        while events:
            event = events.pop(0)
            if not hasattr(event, "player") or event.player.state != HumanPlayer.STATE_DISCONNECTED:
                event.execute()
