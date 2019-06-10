import pytest
from unittest.mock import Mock
from piripherals import Bus


@pytest.fixture
def bus0():
    bus = Mock()
    bus.read_byte_data.side_effect = [24, 42, 0xab, 0xcd, 0, 1]
    bus.read_word_data.return_value = 0xaffe
    bus.read_i2c_block_data.return_value = [1, 2, 3, 4, 5]
    return bus


def test_read_byte(bus0):
    bus = Bus(bus0)
    assert bus.read_byte(0, 1) == 24
    bus0.read_byte_data.assert_called_once_with(0, 1)
    assert bus.read_byte(0, 1) == 42


def test_read_word(bus0):
    bus = Bus(bus0)
    assert bus.read_word(1, 2) == 0xaffe
    bus0.read_word_data.assert_called_once_with(1, 2)


def test_read_block(bus0):
    bus = Bus(bus0)
    assert bus.read_block(8, 7, 5) == [1, 2, 3, 4, 5]
    bus0.read_i2c_block_data.assert_called_once_with(8, 7, 5)


def test_write_byte(bus0):
    bus = Bus(bus0)
    bus.write_byte(3, 4, 66)
    bus0.write_byte_data.assert_called_once_with(3, 4, 66)


def test_write_word(bus0):
    bus = Bus(bus0)
    bus.write_word(6, 8, 0x1234)
    bus0.write_word_data.assert_called_once_with(6, 8, 0x1234)


def test_write_block(bus0):
    bus = Bus(bus0)
    bus.write_block(1, 2, [3, 4, 5])
    bus0.write_i2c_block_data.assert_called_once_with(1, 2, [3, 4, 5])


def test_device_read_byte(bus0):
    dev = Bus(bus0).device(88)
    assert dev.read_byte(23) == 24
    bus0.read_byte_data.assert_called_once_with(88, 23)
    assert dev[3] == 42
    bus0.read_byte_data.assert_called_with(88, 3)


def test_device_read_word(bus0):
    dev = Bus(bus0).device(88)
    assert dev.read_word(42) == 0xaffe
    bus0.read_word_data.assert_called_once_with(88, 42)


def test_device_read_block(bus0):
    dev = Bus(bus0).device(88)
    assert dev.read_block(6, 5) == [1, 2, 3, 4, 5]
    bus0.read_i2c_block_data.assert_called_once_with(88, 6, 5)


def test_device_write_byte(bus0):
    dev = Bus(bus0).device(88)
    dev.write_byte(4, 66)
    bus0.write_byte_data.assert_called_once_with(88, 4, 66)
    dev[11] = 0xcc
    bus0.write_byte_data.assert_called_with(88, 11, 0xcc)


def test_device_write_word(bus0):
    dev = Bus(bus0).device(88)
    dev.write_word(8, 0x1234)
    bus0.write_word_data.assert_called_once_with(88, 8, 0x1234)


def test_device_write_block(bus0):
    dev = Bus(bus0).device(88)
    dev.write_block(2, [3, 4, 5])
    bus0.write_i2c_block_data.assert_called_once_with(88, 2, [3, 4, 5])


@pytest.fixture
def bus1():
    bus = Mock(spec=['read_byte_data', 'write_byte_data'])
    bus.read_byte_data.side_effect = [0xab, 0xcd, 0]
    return bus


def test_read_word2(bus1):
    bus = Bus(bus1)
    assert bus.read_word(0, 0) == 0xab | (0xcd << 8)
    bus1.read_byte_data.assert_any_call(0, 0)
    bus1.read_byte_data.assert_any_call(0, 1)


def test_read_block2(bus1):
    bus = Bus(bus1)
    assert bus.read_block(4, 6, 3) == [0xab, 0xcd, 0]
    bus1.read_byte_data.assert_any_call(4, 6)
    bus1.read_byte_data.assert_any_call(4, 7)
    bus1.read_byte_data.assert_any_call(4, 8)


def test_write_word2(bus1):
    bus = Bus(bus1)
    bus.write_word(0, 0, 0xaffe)
    bus1.write_byte_data.assert_any_call(0, 0, 0xfe)
    bus1.write_byte_data.assert_any_call(0, 1, 0xaf)


def test_write_block2(bus1):
    bus = Bus(bus1)
    bus.write_block(8, 7, [0xde, 0xad, 0xbe, 0xef])
    bus1.write_byte_data.assert_any_call(8, 7, 0xde)
    bus1.write_byte_data.assert_any_call(8, 8, 0xad)
    bus1.write_byte_data.assert_any_call(8, 9, 0xbe)
    bus1.write_byte_data.assert_any_call(8, 10, 0xef)
