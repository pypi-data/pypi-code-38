"""Wrapper classes to abstract bus access."""

from functools import partial
try:
    from smbus import SMBus
except:
    try:
        from smbus2 import SMBus
    except:
        pass

__all__ = ['Bus', 'Device']


class Bus:
    """Abstraction for a data bus, i.e. I2C.

    Args:
        bus: something with read and write methods. It does not have such
            methods, bus is passed to ``SMBus(bus)``.

    The ``bus`` need to have at least the following methods

    - ``read_byte_data(addr,reg)`` -> ``byte``
    - ``write_byte_data(addr,reg,byte)``

    and additionally

    - ``read_word_data(addr,reg)`` -> ``word``
    - ``write_word_data(addr,reg,work)``
    - ``read_i2c_block_data(addr,reg,size)`` -> ``[byte,...]``
    - ``write_i2c_block_data(addr,reg,[byte,...])``

    If these are not present, it will read/write words and blocks using
    ``read_byte_data`` and ``write_byte_data``.

    The bus usually is an ``smbus.SMBus`` or ``smbus2.SMBus`` instance.

    - https://pypi.python.org/pypi/smbus2/
    - https://pypi.python.org/pypi/smbus-cffi/
    - https://packages.debian.org/de/stretch/python-smbus
    """

    def __init__(self, bus=1):
        if not hasattr(bus, 'read_byte_data'):
            bus = SMBus(bus)

        self.read_byte = bus.read_byte_data

        try:
            self.read_word = bus.read_word_data
        except:
            pass

        try:
            self.read_block = bus.read_i2c_block_data
        except:
            pass

        self.write_byte = bus.write_byte_data

        try:
            self.write_word = bus.write_word_data
        except:
            pass

        try:
            self.write_block = bus.write_i2c_block_data
        except:
            pass

    def read_byte(self, addr, reg):
        """read a byte.

        Args:
            addr (int): address of device to read the byte from
            reg (int): register to be read

        Returns:
            int: the byte, that was read
        """
        raise NotImplementedException()

    def read_word(self, addr, reg):
        """read a word (2 bytes).

        Args:
            addr (int): address of device to read the word from
            reg (int): base register, low byte of the word is there,
                high byte is at reg+1

        Returns:
            int: the word, that was read
        """
        return self.read_byte(addr, reg) | self.read_byte(addr, reg + 1) << 8

    def read_block(self, addr, reg, n):
        """read a block of bytes.

        Args:
            addr (int): address of device to read the block from
            reg (int): base register, first byte of the block
            n (int): # of bytes to read n<=32

        Returns:
            list of int: bytes, that were read
        """
        blocks = []
        for i in range(n):
            blocks.append(self.read_byte(addr, reg + i))
        return blocks

    def write_byte(self, addr, reg, byte):
        """write a byte.

        Args:
            addr (int): address of device to write the byte to
            reg (int): register to write to
            byte (int): byte to be written
        """
        raise NotImplementedException()

    def write_word(self, addr, reg, word):
        """write a word (2 bytes).

        Args:
            addr (int): address of device to write the word to
            reg (int): base register, low byte of the word is there,
                high byte is at reg+1
            word (int): word to be written
        """
        self.write_byte(addr, reg, word & 0xff)
        self.write_byte(addr, reg + 1, (word >> 8) & 0xff)

    def write_block(self, addr, reg, block):
        """write a block of bytes.

        Args:
            addr (int): address of device to write the block to
            reg (int): base register, first byte of the block
            block (list of int): bytes to be written, len(block)<=32
        """
        for b in block:
            self.write_byte(addr, reg, b)
            reg += 1

    def device(self, addr):
        """Get a Device.

        Args:
            addr (int): device address

        Returns:
            Device: device at given address
        """
        return Device(self, addr)


class Device:
    """Abstraction of a device on a bus.

    It has the same methods as Bus, but with the ``addr`` already set.

    Args:
        bus (Bus): the bus the Device is attached to
        addr (int): address of the device

    """

    def __init__(self, bus, addr):
        self.read_byte = partial(bus.read_byte, addr)
        self.read_word = partial(bus.read_word, addr)
        self.read_block = partial(bus.read_block, addr)
        self.write_byte = partial(bus.write_byte, addr)
        self.write_word = partial(bus.write_word, addr)
        self.write_block = partial(bus.write_block, addr)

    def __getitem__(self, r): return self.read_byte(r)

    def __setitem__(self, r, b): self.write_byte(r, b)
