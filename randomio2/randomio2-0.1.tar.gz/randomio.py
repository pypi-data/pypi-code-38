#!/usr/bin/env python
"""
Generate test files object easily.
"""
import io
from tempfile import SpooledTemporaryFile
import random
try:
    import faker
except ImportError:
    faker = None

VERSION = (0, 1)
__version__ = '.'.join([str(i) for i in VERSION])
__author__ = 'Anthony Monthe (ZuluPro)'
__email__ = 'anthony.monthe@gmail.com'
__url__ = 'https://github.com/ZuluPro/random-io'
__license__ = 'BSD'


class CharGenerator(io.IOBase):
    """
    Base class to create file object generating an infinity of a single
    character.
    """
    char = None

    def __init__(self, buffering=2**20, char=None):
        self.buffering = buffering
        self.char = char or self.char
        if self.char is None:
            msg = "You must set a `char`"
            raise Exception(msg)

    def read(self, size=None):
        size = size or self.buffering
        return self.char * size


class ZeroGenerator(CharGenerator):
    """
    File object generating an infinity of binary 0.
    """
    char = b'\x00'


class CycleGenerator(io.IOBase):
    """
    Base class to create file object generating an infinity of a multiple
    characters.
    """
    chars = None

    def __init__(self, buffering=2**20, chars=None):
        self.buffering = buffering
        self.chars = chars or self.chars
        if self.chars is None:
            msg = "You must set a `chars`"
            raise Exception(msg)

    def read(self, size=None):
        size = size or self.buffering
        string = ''
        for _ in range(size):
            string += random.choice(self.chars)
        return string


class BinaryGenerator(CycleGenerator):
    """
    File object generating an infinity of binary 0 & 1.
    """
    chars = '\x00\x01'


class FileGenerator(io.IOBase):
    """
    File object generating a fixed size from a generator.
    """
    mode = 'rb'

    def __init__(self, size=128, source=None):
        """
        :param size: File size
        :type size: int

        :param source: Generator class by default ZeroGenerator
        :type source: Generator
        """
        self.size = size
        self.offset = 0
        self.source = ZeroGenerator() if source is None else source

    def read(self, size=None):
        if self.offset >= self.size:
            return b''
        left = self.size - self.offset
        if size is None:
            self.offset = self.size
            return self.source.read(left)
        else:
            self.offset += size
            if self.offset > self.size:
                self.offset = self.size
            return self.source.read(size)[:left]

    def readable(self):
        return True

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.size - offset

    def close(self):
        self.source.close()

    @property
    def closed(self):
        return self.source.closed

    def tell(self):
        return self.offset


class LoremIpsumGenerator(FileGenerator):
    """
    File object generating random words.
    """
    def __init__(self, size=1):
        """
        :param size: File size
        :type size: int
        """
        if faker is None:
            msg = "You must install 'faker' for this Generator."
            raise Exception(msg)
        self.faker = faker.Faker()
        self.words = self.faker.sentence(100000)
        super(LoremIpsumGenerator, self).__init__(size=size, source=None)

    def read(self, size=None):
        if self.offset >= self.size:
            return ''
        left = self.size - self.offset
        if size is None:
            self.offset = self.size
            words = SpooledTemporaryFile(max_size=1024, mode='w+')
            words_len = 0
            while words_len < left:
                words.write(self.words + ' ')
                words_len += len(self.words + ' ')
            words.seek(0)
            return words.read()[:left]
        else:
            self.offset += size
            if self.offset > self.size:
                self.offset = self.size
            words = SpooledTemporaryFile(mode='w+')
            words_len = 0
            while words_len < size:
                words.write(self.words + ' ')
                words_len += len(self.words + ' ')
            words.seek(0)
            return words.read(size)[:left]
