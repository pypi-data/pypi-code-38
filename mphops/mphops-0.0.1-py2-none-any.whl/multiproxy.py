# IPv8 node
# ----------------------------------------------------------------------------------------------------------------------
# For peer discovery ...

import logging
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.python import log

from ipv8lib.ipv8.messaging.anonymization.community import TunnelCommunity, TunnelSettings
from ipv8lib.ipv8.messaging.anonymization.tunnel import CIRCUIT_STATE_READY, PEER_FLAG_EXIT_ANY
from ipv8lib.ipv8.peer import Peer
from socks5_ipv8.hops.daemon import read_config
from socks5_ipv8.hops.forwarder_factory import ForwardFactory
from socks5_ipv8.hops.server_factory import ServerFactory
from socks5_ipv8.hops.socks5_factory import Socks5Factory

master_peer_init = Peer(
    "307e301006072a8648ce3d020106052b81040024036a00040112bc352a3f40dd5b6b34f28c82636b3614855179338a1c2f9ac87af17f5af3084955c4f58d9a48d35f6216aac27d68e04cb6c200025046155983a3ae1378320d93e3d865c6ab63b3f11a6c74fc510fa67b2b5f448de756b4114f765c80069e9faa51476604d9d4"
        .decode('HEX'))


class MultiProxy(TunnelCommunity):
    master_peer = master_peer_init

    def __init__(self, my_peer, endpoint, network):
        super(MultiProxy, self).__init__(my_peer, endpoint, network)
        self.peers_dict = {}
        self.socks5_factory = Socks5Factory(self)

        self.config = read_config()
        self.addr, self.port = self.endpoint.get_address()
        self.socks5_port = None

    @inlineCallbacks
    def get_socks5server_port(self):
        port = yield self.open_socks5_server()
        self.socks5_port = port

    def open_socks5_server(self):
        port = self.config['socks5_port']
        for _ in range(100):
            try:
                reactor.listenTCP(port, self.socks5_factory)
                break
            except:
                port += 1
                continue
        logging.info("socks5_twisted server listening at port {}".format(port))
        self.socks5_port = port
        return port

    def started(self):
        def start_communication():
            # print "I am:", self.my_peer, "\nI know:", [str(p) for p in self.get_peers()]
            for p in self.get_peers():
                if p not in self.peers_dict:
                    self.logger.info("New Host {} join the network".format(p))
                self.peers_dict[p] = None

        self.register_task("start_communication", LoopingCall(start_communication)).start(5.0, True).addErrback(log.err)
        self.register_task("check_circuit", LoopingCall(self.check_circuit)).start(2.0, True).addErrback(log.err)
        # self.register_task("tunnels_ready", LoopingCall(self.tunnels_ready).start(5.0, True).addErrback(log.err))

    def check_circuit(self):
        """
        Implemented by MultiProxyClient
        """
        pass


class MultiProxyClient(MultiProxy):

    def __init__(self, my_peer, endpoint, network):
        super(MultiProxyClient, self).__init__(my_peer, endpoint, network)
        self.settings = TunnelSettings()
        self.remove_tunnel_delay = 1000
        self.max_joined_circuits = 1000
        self.forward_factory = ForwardFactory(self)
        reactor.listenTCP(self.port, self.forward_factory)

    def check_circuit(self):
        # Update first hop address
        for circuit_id, circuit in self.circuits.items():
            # check if the circuit is ready
            if circuit.state == CIRCUIT_STATE_READY:
                self.logger.debug("{}:{}, {}, Get new circuit {};{};{}"
                                  .format(self.addr, self.port, self.__class__.__name__,
                                          self.circuits, self.relay_from_to, self.exit_sockets, ))
                first_hops = [v.peer.address for k, v in self.circuits.items()]
                self.logger.debug("{}:{}, {}, First hop address is {}"
                                  .format(self.addr, self.port, self.__class__.__name__, first_hops))

                self.socks5_factory.circuit_peers[circuit_id] = circuit
                # Open socks5 server port once a circuit is built
                if not self.socks5_port:
                    self.get_socks5server_port()
                    self.logger.debug("{}:{}, {}, Initialized at {}"
                                      .format(self.addr, self.port, self.__class__.__name__, self.socks5_port))

        self.logger.debug("{}:{}, {}, Update first hop {}"
                          .format(self.addr, self.port, self.__class__.__name__, self.socks5_factory.circuit_peers))

        # Update forwarder addresses
        for circuit_id, relay_route in self.relay_from_to.items():
            forwarder_address = relay_route.peer.address
            self.forward_factory.circuit_peers[circuit_id] = forwarder_address
        self.logger.debug("{}:{}, {}, Update forward address {}"
                          .format(self.addr, self.port, self.__class__.__name__, self.forward_factory.circuit_peers))

        # Update exit nodes
        self.update_exit_node(self.socks5_factory)
        exit_node = self.socks5_factory.exit_node.values()[0] if self.socks5_factory.exit_node else 'None'
        self.logger.debug("{}:{}, {}, Update exit nodes {}"
                          .format(self.addr, self.port, self.__class__.__name__, exit_node))

        self.update_exit_node(self.forward_factory)
        exit_node = self.forward_factory.exit_node.values()[0] if self.socks5_factory.exit_node else 'None'
        self.logger.debug("{}:{}, {}, Update exit nodes {}"
                          .format(self.addr, self.port, self.__class__.__name__, exit_node))

    def update_exit_node(self, factory):
        for key, peer in self.exit_sockets.items():  # change to exit_socket?
            print key, peer
            exit_address = peer.address
            if key not in factory.exit_node:
                factory.exit_node[key] = exit_address

    def update_address(self, cid, peer):
        self.forward_factory.circuit_peers[cid] = peer

    def update_id(self, idx, new_idx):
        self.forward_factory.circuit_id[idx] = new_idx


class MultiProxyInitiator(MultiProxyClient):

    def __init__(self, my_peer, endpoint, network):
        super(MultiProxyInitiator, self).__init__(my_peer, endpoint, network)

        self.build_tunnels(1)


class MultiProxyForwarder(MultiProxyClient):

    def __init__(self, my_peer, endpoint, network):
        super(MultiProxyForwarder, self).__init__(my_peer, endpoint, network)


class MultiProxyServer(MultiProxy):

    def __init__(self, my_peer, endpoint, network):
        super(MultiProxyServer, self).__init__(my_peer, endpoint, network)
        self.settings = TunnelSettings()
        self.remove_tunnel_delay = 1000
        self.max_joined_circuits = 1000
        self.settings.peer_flags = PEER_FLAG_EXIT_ANY
        self.server_factory = ServerFactory(self)
        reactor.listenTCP(self.port, self.server_factory)
