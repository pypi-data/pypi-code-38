"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

@TODO: test id's when packets are implemented
"""
from unittest import TestCase

from pynetworking.ID_management import *
from pynetworking.Packets import FunctionPacket, DataPacket, Packet, Header
from pynetworking.Data import ByteStream
from pynetworking.Logging import logger


class TestIDManager(TestCase):

    def doCleanups(self):
        remove_manager(0)
        remove_manager(1)
        remove_manager(2)

    def test_multiple_same_managers(self):
        manager1_0 = IDManager(1)
        manager1_1 = IDManager(1)
        self.assertEqual(manager1_0, manager1_1)

    def test_multiple_different_managers(self):
        manager1 = IDManager(1)
        manager2 = IDManager(2)
        self.assertNotEqual(manager1, manager2)

    def test_remove_manager(self):
        manager1_0 = IDManager(1)
        remove_manager(1)
        manager1_1 = IDManager(1)
        self.assertNotEqual(manager1_0, manager1_1)

    def test_one_func_packet(self):
        packet = FunctionPacket("dummy")
        IDManager(0).set_ids_of_packet(packet)
        expected_ids = (0, 0)
        self.assertEqual(expected_ids, packet.header.id_container.get_ids())
        expected_function_stack = [0]
        self.assertEqual(expected_function_stack, IDManager(0).get_function_stack())

    def test_func_data(self):
        func_packet = FunctionPacket("dummy")
        IDManager(0).set_ids_of_packet(func_packet)

        data_packet = DataPacket(ret="Nothing")
        IDManager(0).set_ids_of_packet(data_packet)
        expected_ids = (0, 1)
        self.assertEqual(expected_ids, data_packet.header.id_container.get_ids())
        expected_function_stack = []
        self.assertEqual(expected_function_stack, IDManager(0).get_function_stack())

    def test_func_func_data_data(self):
        self.assertEqual([], IDManager(0).get_function_stack())

        func_packet_0 = FunctionPacket("dummy")
        IDManager(0).set_ids_of_packet(func_packet_0)
        self.assertEqual((0, 0), func_packet_0.header.id_container.get_ids())
        self.assertEqual([0], IDManager(0).get_function_stack())

        func_packet_1 = FunctionPacket("Dummy")
        IDManager(0).set_ids_of_packet(func_packet_1)
        self.assertEqual((1, 1), func_packet_1.header.id_container.get_ids())
        self.assertEqual([0, 1], IDManager(0).get_function_stack())

        data_packet_1 = DataPacket(ret="Nothing")
        IDManager(0).set_ids_of_packet(data_packet_1)
        self.assertEqual((1, 2), data_packet_1.header.id_container.get_ids())
        self.assertEqual([0], IDManager(0).get_function_stack())

        data_packet_0 = DataPacket(ret="Nothing")
        IDManager(0).set_ids_of_packet(data_packet_0)
        self.assertEqual((0, 3), data_packet_0.header.id_container.get_ids())
        self.assertEqual([], IDManager(0).get_function_stack())

    def test_packing(self):
        """
        client        -    server
            func --->
                        <---func
            data --->
                        <---data
        """
        # --------client----------- send func
        func_packet_0 = FunctionPacket("N")
        IDManager(0).set_ids_of_packet(func_packet_0)
        bytes_ = func_packet_0.pack()
        self.assertEqual((0, 0), func_packet_0.header.id_container.get_ids())
        self.assertEqual([0], IDManager(0).get_function_stack())

        # --------server--------- recv func, send func
        byte_stream = ByteStream(bytes_)
        header = Header.from_bytes(byte_stream)
        packet = Packet.from_bytes(header, byte_stream)
        IDManager(1).update_ids_by_packet(packet)
        self.assertEqual((0, 0), packet.header.id_container.get_ids())
        self.assertEqual([0], IDManager(1).get_function_stack())

        func_packet_1 = FunctionPacket("W")
        IDManager(1).set_ids_of_packet(func_packet_1)
        bytes_ = func_packet_1.pack()
        self.assertEqual((1, 1), func_packet_1.header.id_container.get_ids())
        self.assertEqual([0, 1], IDManager(1).get_function_stack())

        # --------client----------- recv func, send data
        byte_stream = ByteStream(bytes_)
        header = Header.from_bytes(byte_stream)
        packet = Packet.from_bytes(header, byte_stream)
        IDManager(0).update_ids_by_packet(packet)
        self.assertEqual((1, 1), packet.header.id_container.get_ids())
        self.assertEqual([0, 1], IDManager(0).get_function_stack())

        data_packet_1 = DataPacket(ret="Nothing")
        IDManager(0).set_ids_of_packet(data_packet_1)
        bytes_ = data_packet_1.pack()
        self.assertEqual((1, 2), data_packet_1.header.id_container.get_ids())
        self.assertEqual([0], IDManager(0).get_function_stack())

        # --------server--------- recv data, send data
        byte_stream = ByteStream(bytes_)
        header = Header.from_bytes(byte_stream)
        packet = Packet.from_bytes(header, byte_stream)
        IDManager(1).update_ids_by_packet(packet)
        self.assertEqual((1, 2), packet.header.id_container.get_ids())
        self.assertEqual([0], IDManager(1).get_function_stack())

        data_packet_0 = DataPacket(ret="Nothing")
        IDManager(1).set_ids_of_packet(data_packet_0)
        bytes_ = data_packet_0.pack()
        self.assertEqual((0, 3), data_packet_0.header.id_container.get_ids())
        self.assertEqual([], IDManager(1).get_function_stack())

        # --------client----------- recv data
        byte_stream = ByteStream(bytes_)
        header = Header.from_bytes(byte_stream)
        packet = Packet.from_bytes(header, byte_stream)
        IDManager(0).update_ids_by_packet(packet)
        self.assertEqual((0, 3), packet.header.id_container.get_ids())
        self.assertEqual([], IDManager(0).get_function_stack())
