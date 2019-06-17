"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:

"""
import unittest

from pynetworking.Packets import Header, Packet, DataPacket, FunctionPacket, FileMetaPacket
from pynetworking.Data import ByteStream
from pynetworking.Logging import logger

from pynetworking.tests.example_functions import DummyPerson


class TestPackets(unittest.TestCase):

    def helper_packet_tests(self, packet):
        packet_one = packet
        byte_string = packet_one.pack()
        byte_stream = ByteStream(byte_string)
        header = Header.from_bytes(byte_stream)
        packet_two = Packet.from_bytes(header, byte_stream)
        self.assertEqual(packet_one, packet_two)

    def test_function_packet(self):
        packet = FunctionPacket(example_function, "John", "Miller", (12, 13))
        self.helper_packet_tests(packet)

        packet = FunctionPacket(example_function, "John", tup=("HE",))
        self.helper_packet_tests(packet)

    def test_function_packet_class_arg(self):
        packet = FunctionPacket(example_function, DummyPerson("He", 12))
        self.helper_packet_tests(packet)

    def test_data_packet(self):
        packet = DataPacket(Name="John Miller")
        self.helper_packet_tests(packet)

        packet = DataPacket(username="John", age="28", password={"val": ["he", "he"], "val2": (2, (3, 5))})
        self.helper_packet_tests(packet)

        packet = DataPacket(classObj=TestHeader)
        self.helper_packet_tests(packet)

    def test_file_meta_packet(self):
        packet = FileMetaPacket(r"C:\Hello\World\src.txt", 0, "D:/WOW/dst.txt")
        self.helper_packet_tests(packet)

        packet = FileMetaPacket(r"C:\Hello\World\src.txt", 0)
        self.helper_packet_tests(packet)


class TestHeader(unittest.TestCase):

    def test_packing(self):
        packet = DataPacket(Test=10)
        header1_0 = packet.header
        byte_string = packet.pack()
        byte_stream = ByteStream(byte_string)
        header1_1 = Header.from_bytes(byte_stream)
        self.assertEqual(header1_0, header1_1)


def example_function(name, second_name="Miller", tup=()):
    print("Hello: " + str(name) + " " + str(second_name) + " --> " + str(tup))
