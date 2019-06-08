import logging
from .base import MUDObject
from .servers import MUDSocket
from .channel import Channel

class MUDInterfaces(MUDObject):

    def __init__(self, engine):

        from .base import MetaMUDInterface

        for iface_name, iface in MetaMUDInterface._INTERFACES.items():
            iface.engine = engine
            setattr(self, iface_name, iface)

            # Add the other interfaces as attributes to this interface (easier when looking stuff up)
            for oface_name, oface in MetaMUDInterface._INTERFACES.items():
                setattr(iface, oface_name, oface)

class MUDEngine(MUDObject):

    _PULSE = 1 # 1 beat per second

    _INSTANCE = None

    shutdown = False

    def __init__(self, host="localhost", port=5000):
        self.port = port
        self.host = host
        self.socket = MUDSocket()
        self.players = []
        self.events = []
        self.channels = {"general": Channel("general")}
        self.interfaces = MUDInterfaces(self)
        self.__class__._INSTANCE = self

    def run(self):

        logging.info("Running godwars on {}:{}".format(self.host, self.port))
        self.socket.bind_and_listen(self.host, self.port)
        while True:
            self.handle_events()
            self.socket.handle_incoming_connections()
            self.socket.handle_incoming_messages()
            if self.shutdown:
                logging.info("Shutdown command received, shutting down")
                return

    def disconnect_player(self, player):

        logging.debug("Disconnecting player {}".format(player))
        self.players.remove(player)
        self.socket.clients.remove(player.client)
        del player.client
        del player

    def connect_player(self, player):
        self.players.append(player)

    def handle_events(self):
        events = self.events
        self.events = []
        while events:
            events.pop(0).execute()
