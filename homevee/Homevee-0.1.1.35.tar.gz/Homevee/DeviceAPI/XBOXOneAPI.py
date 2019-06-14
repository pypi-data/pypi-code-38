import select
import socket
import sys
import time

from Homevee.Helper import Logger

XBOX_PORT = 5050
XBOX_PING = "dd00000a000000000000000400000002"

py3 = sys.version_info[0] > 2

class XBOXOneAPI:
    def __init__(self):
        return

    def xbox_wake_up(self, ip_address, live_id):
        Logger.log("Starting Xbox")

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(0)
        s.bind(("", 0))
        s.connect((ip_address, XBOX_PORT))

        if isinstance(live_id, str):
            live_id = live_id.encode()
        else:
            live_id = live_id

        power_payload = b'\x00' + chr(len(live_id)).encode() + live_id + b'\x00'
        power_header = b'\xdd\x02\x00' + chr(len(power_payload)).encode() + b'\x00\x00'
        power_packet = power_header + power_payload
        Logger.log("Sending power on packets to {0}...".format(ip_address))
        self.send_power(s, power_packet)
        # ping_result = send_ping(s)

        s.close()


    def send_power(self, s, data, times=5):
        for i in range(0, times):
            s.send(data)
            time.sleep(1)


    def send_ping(self, s):
        s.send(bytearray.fromhex(XBOX_PING))
        return select.select([s], [], [], 5)[0]
