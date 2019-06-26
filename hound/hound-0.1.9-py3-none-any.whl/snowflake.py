## Encode 22-byte snowflake into 44 byte (hex encoded) object name
## * 64-bit (8 byte) timestamp (encoded as python double-precision struct)
## * 64-bit (8 byte) machine id (based on nodename) Only 6 bytes used
## * 16-bit (2 byte) random client id (generated during init of Snowflake object)
## * 16-bit (2 byte) sequence identifier (starts at 0 per client, increments from there)
## * 8-bit (1 byte) Zero field (reserved)
## * 8-bit (1 byte) checksum field (sum of remaining fields)

import struct
import time
from threading import RLock
from uuid import getnode
import os
from functools import lru_cache
from collections import namedtuple

Snowflake = namedtuple('Snowflake', ['time', 'machine_id', 'client_id', 'sequence_id'])

@lru_cache(None) # unbounded
def getclient(name="__COMMON__"):
    """
    Generates a new Snowflake client for your program
    It's best to share one client, but in case you need multiple, you can
    specify a different client name.

    Calling getclient() with the same name will return the same client
    """

    return SnowflakeClient(name=name)

class SnowflakeClient(object):

    # by using big-endian ordering, snowflake bytes can be directly sorted
    # since the timestamp will be in the proper byte-order for sorting
    FORMAT = '>dQHHxB'
    HEAD_FORMAT = '>dQHHx'

    def __init__(self, name):
        """
        Constructs a new snowflake client
        It's preferred that you use getclient() to share a client within your
        application, but not required.

        Multiple clients will still produce valid snowflakes
        """
        self.name = name
        self.lock = RLock()
        self.last_time = time.time()
        self.machine_id = getnode()
        self.client_id = struct.unpack('<H', os.urandom(2))[0]
        self.sequence_id = 0
        self.offset = time.localtime().tm_gmtoff

    def __repr__(self):
        return "<hound.SnowflakeClient {}>".format(self.name)

    def __call__(self):
        """
        Returns a new valid snowflake as bytes

        Prevents rollback by ensuring the timestamp field occurs after this client's
        most recent snowflake
        """
        with self.lock:
            ctime = time.time()
            while ctime < self.last_time:
                time.sleep(0.05 + (self.last_time - ctime))
                ctime = time.time()
            head = struct.pack(
                self.HEAD_FORMAT,
                ctime,
                self.machine_id,
                self.client_id,
                self.sequence_id,
            )
            checksum = sum(head) % 256
            out = head + bytes([checksum])
            self.sequence_id = (self.sequence_id + 1) % 65536
            self.last_time = ctime
            return out

    snowflake = __call__

    def unpack(self, snowflake, validate=True):
        """
        Unpacks a snowflake into it's components
        Returns a namedtuple
        If validate is True (default), raise an error if the checksum is not valid
        """
        if isinstance(snowflake, str):
            snowflake = bytes.fromhex(snowflake)
        elif not isinstance(snowflake, bytes):
            raise TypeError("snowflake must be of type str or bytes")
        ctime, machine_id, client_id, sequence_id, checksum = struct.unpack(
            self.FORMAT,
            snowflake
        )
        if validate and (sum(snowflake[:-2]) % 256) != checksum:
            raise ValueError("Snowflake {} is not valid".format(snowflake.hex()))
        return Snowflake(
            ctime,
            machine_id,
            client_id,
            sequence_id
        )
