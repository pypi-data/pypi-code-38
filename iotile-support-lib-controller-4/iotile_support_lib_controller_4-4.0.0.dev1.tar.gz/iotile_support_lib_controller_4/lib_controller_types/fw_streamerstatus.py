import struct
import datetime
from iotile.core.hw.exceptions import *
from iotile.core.exceptions import *
from . import fw_tileselector

class StreamerStatus:
    """

    """

    def __init__(self, binvalue):
        last_attempt, last_success, last_error, highest_ack, last_status, attempt, comm = struct.unpack("<LLLLBBBx", binvalue)

        self.last_attempt = last_attempt
        self.last_success = last_success
        self.last_status = last_status
        self.last_error = last_error
        self.attempt_num = attempt
        self.comm_status = comm
        self.highest_ack_received = highest_ack

    def __str__(self):
        output  = ""
        output += "SensorGraph Streamer\n"
        output += "Last successful stream: %d\n" % self.last_success
        output += "Last streaming attempt: %d\n" % self.last_attempt
        output += "Last streaming result: %d\n" % self.last_status
        output += "Last streaming error: %d\n" % self.last_error
        output += "Backoff attempt number: %d\n" % self.attempt_num
        output += "Current CommStream state: %d\n" % self.comm_status
        output += "Highest ACK received: %d\n" % self.highest_ack_received

        return output

def size():
    return 20

def convert(arg):
    if isinstance(arg, StreamerStatus):
        return arg

    raise ValueError("fw_streamerstatus can only be created from binary data inside a bytearray")

def convert_binary(arg, **kwargs):
    return StreamerStatus(arg)

#Formatting Functions
def default_formatter(arg, **kwargs):
    return str(arg)
