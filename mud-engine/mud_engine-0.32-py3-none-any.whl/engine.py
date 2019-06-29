import logging
from .base import MUDObject
from .base import MUDInterface
from .servers import MUDTelnetServer
from .base import StopAction
from .player import HumanPlayer
from .player import ConnectingPlayer
import time

class MUDEngine(MUDObject):

    pulse = 1.5 * 1000000000 # 1 beat per 1.5 seconds
    _last_heartbeat = 0 # Nanoseconds since last heartbeat
    _instance = None

    shutdown = None
    name = "MUDEngine"

    players = []

    def __init__(self, host="localhost", port=5000):
        self.port = port
        self.host = host
        self.server = MUDTelnetServer()
        self.admins = [] # A list of names to make admins
        self.events = []
        self.geography = []
        self.channels = {}
        self.interface = MUDInterface()
        MUDInterface.engine = self

        logging.info("Loading geography data")
        self.interface.geography.load_geography()

        logging.info("Loading communication channels")
        self.channels = self.interface.channel.load_channels()
        MUDEngine._instance = self

    def run(self):

        logging.info("Running {} on {}:{}".format(self.name, self.host, self.port))
        self.server.bind_and_listen(self.host, self.port)

        self._last_heartbeat = time.time_ns()

        while True:

            t = time.time_ns()
            if t - self._last_heartbeat > self.pulse:
                self.heartbeat()
                self._last_heartbeat = t

            self.handle_events()
            self.server.handle_incoming_connections()
            self.server.handle_incoming_messages()

            if self.shutdown is None:
                continue

            if self.shutdown == 0:
                logging.info("Shutdown command received, shutting down")
                return

    def get_connected_players(self):
        return [v for v in self.players if v.connected]

    def heartbeat(self):

        for obj, heartbeat in [(k,v) for k,v in MUDObject._heartbeats.items()]:
            if obj != self:
                heartbeat()

        if self.shutdown is None:
            return

        from mud_engine.communication import Red
        from mud_engine.communication import NoColor

        self.interface.channel.get_channel_by_name("general")\
            .queue_message(f"{Red}Server shutting down in {self.shutdown} heartbeats{NoColor}", prompt=False)
        self.shutdown -= 1

    @classmethod
    def add_player(self, player):

        # This is a bit hackish, act like a instance method when the engine has been instantiated
        # otherwise it's a class method. Need to be able to add NPCs before and after instantiation

        if self._instance:
            self = self._instance

        from .npc import NPC

        if isinstance(player, NPC):
            self.players.append(player)
        else:
            if player.name not in [v.name for v in self.players]:
                self.players.append(player)
            else:
                logging.debug(f"Attempted to add player {player} that is already in the engine")


    def disconnect_player(self, player):

        logging.info("Disconnecting player {}".format(player))
        player.connected = False
        if player.location:
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

        if player.name.lower() in self.admins:
            logging.info("Admin logging in {}".format(player.name))
            player.admin = True

        self.add_player(player)

        if not player.location:
            player.set_location(self.geography[0])
        else:
            player.set_location(player.location)

        player.queue_message(f"Welcome to {self.name}, {player.name}", prompt=False)

        self.interface.channel.add_player_to_valid_channels(player)

        player.location.render_to_player(player)

    def handle_events(self):
        events = self.events
        self.events = []
        while events:
            event = events.pop(0)
            if not hasattr(event, "player") \
                    or (isinstance(event.player, HumanPlayer) and event.player.connected) \
                    or (isinstance(event.player, ConnectingPlayer) \
                        and event.player.login_state != ConnectingPlayer.LOGIN_STATE_CONNECTED):
                event.execute()
