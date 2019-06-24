import unittest
import bzenet

class TestAddress(unittest.TestCase):
    def test_host(self):
        self.assertEquals(bzenet.Address("127.0.0.1", 9999).host, "127.0.0.1")
        self.assertEquals(bzenet.Address("localhost", 9999).host, "127.0.0.1")
        self.assertEquals(bzenet.Address(None, 9999).host, "*")
        self.assertRaises(IOError, bzenet.Address, "foo.bar.baz.999", 9999)

    def test_port(self):
        self.assertEquals(bzenet.Address("127.0.0.1", 9999).port, 9999)
        self.assertRaises(TypeError, bzenet.Address, "127.0.0.1", "foo")

    def test_hostname(self):
        import socket
        self.assertEquals(bzenet.Address(socket.gethostname(), 9999).hostname, socket.gethostname())
        self.assertEquals(bzenet.Address(None, 9999).hostname, "*")

    def test_str(self):
        self.assertEquals(bzenet.Address("127.0.0.1", 9999).__str__(), "127.0.0.1:9999")

    def test_richcmp(self):
        self.assertTrue(bzenet.Address("127.0.0.1", 9999) == bzenet.Address("127.0.0.1", 9999))
        self.assertTrue(bzenet.Address("127.0.0.1", 9999) != bzenet.Address("127.0.0.1", 8888))
        self.assertFalse(bzenet.Address("127.1.1.1", 1992) == bzenet.Address("127.0.0.1", 9999))

class TestPacket(unittest.TestCase):
    def test_data(self):
        self.assertEquals(bzenet.Packet(b"foo\0bar").data, b"foo\0bar")
        self.assertRaises(MemoryError, getattr, bzenet.Packet(), "data")

    def test_dataLength(self):
        self.assertEquals(bzenet.Packet(b"foobar").dataLength, 6)
        self.assertEquals(bzenet.Packet(b"foo\0bar").dataLength, 7)
        self.assertRaises(MemoryError, getattr, bzenet.Packet(), "dataLength")

    def test_flags(self):
        self.assertEquals(bzenet.Packet(b"foobar").flags, 0)
        self.assertEquals(bzenet.Packet(b"foobar", bzenet.PACKET_FLAG_UNSEQUENCED).flags, bzenet.PACKET_FLAG_UNSEQUENCED)
        self.assertRaises(MemoryError, getattr, bzenet.Packet(), "flags")

class TestHost(unittest.TestCase):
    def setUp(self):
        self.client = bzenet.Host(None, 1, 0, 0, 0)
        self.server = bzenet.Host(bzenet.Address("localhost", 54301), 1, 0, 0, 0)
        self.peer = self.client.connect(bzenet.Address("localhost", 54301), 1)
        self.assertEquals(self.peer.state, bzenet.PEER_STATE_CONNECTING)

    def tearDown(self):
        del self.client
        del self.server
        del self.peer

    def test_connect(self):
        client_connected = False
        server_connected = False

        counter = 0
        while counter < 100 or not (client_connected and server_connected):
            event = self.client.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)
                client_connected = True
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)
                server_connected = True
            counter += 1

        self.assertEquals(client_connected, True)
        self.assertEquals(server_connected, True)

    def test_socketsend(self):

        self.send_done = False
        socketsend_msg = b"\xff\xff\xff\xffgetstatus\x00"

        def f(address, data):
            if data != socketsend_msg:
                # error messages are not propagating
                # through cython
                print("data != statusResponse")
                assert(False)
            self.send_done = True

        while not self.send_done:

            self.client.service(0)
            self.client.socket.send(self.server.address, socketsend_msg)

            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.server.intercept = f


    def test_broadcast(self):
        broadcast_done = False
        broadcast_msg = b"foo\0bar\n baz!"

        while not broadcast_done:
            event = self.client.service(0)
            if event.type == bzenet.EVENT_TYPE_RECEIVE:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)
                self.assertEquals(event.packet.data, broadcast_msg)
                broadcast_done = True
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)
                self.server.broadcast(0, bzenet.Packet(broadcast_msg))

class TestPeer(unittest.TestCase):
    def setUp(self):
        self.client = bzenet.Host(None, 1, 0, 0, 0)
        self.server = bzenet.Host(bzenet.Address("localhost", 54301), 1, 0, 0, 0)
        self.peer = self.client.connect(bzenet.Address("localhost", 54301), 1)
        self.assertEquals(self.peer.state, bzenet.PEER_STATE_CONNECTING)
        self.assertTrue(self.peer == self.peer)
        self.assertFalse(self.peer != self.peer)

    def tearDown(self):
        del self.client
        del self.server
        del self.peer

    def test_access(self):
        self.assertRaises(MemoryError, bzenet.Peer().reset)

    def test_send(self):
        msg = b"foo\0bar"
        msg_received = False

        while not msg_received:
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_RECEIVE:
                msg_received = True
                self.assertEquals(event.packet.data, msg)

            event = self.client.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                packet = bzenet.Packet(msg)
                self.assertEquals(packet.sent, False)
                ret = self.peer.send(0, packet)
                self.assertEquals(ret, 0)
                self.assertEquals(packet.sent, True)

    def test_reset(self):
        reset_done = False
        while not reset_done:
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)
                event.peer.reset()
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_DISCONNECTED)
                reset_done = True
            event = self.client.service(0)

    def test_disconnect(self):
        connected = True
        while connected:
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_DISCONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_DISCONNECTED)
                connected = False
            elif event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(self.peer.state, bzenet.PEER_STATE_CONNECTED)
                self.peer.disconnect()
                self.assertEquals(self.peer.state, bzenet.PEER_STATE_DISCONNECTING)

            event = self.client.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)

    def test_disconnect_later(self):
        connected = True
        while connected:
            event = self.server.service(0)
            if event.type == bzenet.EVENT_TYPE_DISCONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_DISCONNECTED)
                connected = False
            elif event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(self.peer.state, bzenet.PEER_STATE_CONNECTED)
                self.peer.disconnect_later()
                self.assertEquals(self.peer.state, bzenet.PEER_STATE_DISCONNECT_LATER)

            event = self.client.service(0)
            if event.type == bzenet.EVENT_TYPE_CONNECT:
                self.assertEquals(event.peer.state, bzenet.PEER_STATE_CONNECTED)

if __name__ == '__main__':
    unittest.main()
