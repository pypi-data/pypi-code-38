import logging
from .base import MUDObject
from .base import MUDInterface
from .servers import MUDTCPSocket

class MUDEngine(MUDObject):

    _PULSE = 1 # 1 beat per second

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

    def run(self):

        logging.info("Loading geography data")
        self.interface.geography.load_geography()

        logging.info("Loading communication channels")
        self.channels = self.interface.channel.load_channels()

        logging.info("Running {} on {}:{}".format(self.name, self.host, self.port))
        self.socket.bind_and_listen(self.host, self.port)

        while True:
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
            events.pop(0).execute()
