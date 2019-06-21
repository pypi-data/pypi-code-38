import logging
from .base import MUDObject
from .base import MUDInterface
from .servers import MUDTelnetServer
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
        self.server = MUDTelnetServer()
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
        self.server.bind_and_listen(self.host, self.port)

        self._LAST_HEARTBEAT = time.time_ns()

        while True:

            t = time.time_ns()
            if t - self._LAST_HEARTBEAT > self.pulse:
                self.heartbeat()
                self._LAST_HEARTBEAT = t

            self.handle_events()
            self.server.handle_incoming_connections()
            self.server.handle_incoming_messages()

            if not self.shutdown:
                continue
            if self.shutdown == 3:
                logging.info("Shutdown command received, shutting down")
                return
            self.interface.channel.get_channel_by_name("general").send_message("Server shutting down in {}".format(self.shutdown), prompt=False)
            self.shutdown += 1

    def get_connected_players(self):
        return [v for v in self.players if v.connected]

    def heartbeat(self):
        for obj, heartbeat in [(k,v) for k,v in _HEARTBEATS.items()]:
            if obj != self:
                heartbeat()

    def add_player(self, player):
        if player.name not in [v.name for v in self.players]:
            self.players.append(player)
        else:
            logging.warning("Attempted to add a player that is already in the engine")


    def disconnect_player(self, player):

        logging.info("Disconnecting player {}".format(player))
        player.connected = False
        player.location.players.remove(player)
        for channel in player.channels:
            channel.players.remove(player)
        player._deregister_heartbeat()
        self.server.clients.remove(player.client)
        del player.client
        import gc
        gc.collect()

    def connect_player(self, player):
        logging.info("Logging in player {}".format(player))
        player.connected = True
        self.add_player(player)
        if not player.location:
            player.set_location(self.geography[0])
        player.location.render_to_player(player)

    def handle_events(self):
        events = self.events
        self.events = []
        while events:
            event = events.pop(0)
            if not hasattr(event, "player") or (event.player.connected or event.player.login_state != HumanPlayer.LOGIN_STATE_CONNECTED):
                event.execute()
