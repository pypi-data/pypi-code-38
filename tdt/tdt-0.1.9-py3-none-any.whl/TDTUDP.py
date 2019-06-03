import socket
import struct
import time

import tdt

class TDTUDP():
    def __init__(self, host='10.1.0.100', send_type=float, recv_type=float, verbose=False):

        self.NPACKETS = -1
        self.send_header = None

        self.TDT_UDP_HOSTNAME = host
        self.send_type = send_type
        self.recv_type = recv_type
        self.verbose = verbose

        # UDP command constants
        self.CMD_SEND_DATA        = 0x00
        self.CMD_GET_VERSION      = 0x01
        self.CMD_SET_REMOTE_IP    = 0x02
        self.CMD_FORGET_REMOTE_IP = 0x03

        # Important: the RZ UDP interface port is fixed at 22022
        self.UDP_PORT = 22022

        # create a UDP socket object
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # UDP

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # connect the PC to the target UDP interface
        self.sock.connect((self.TDT_UDP_HOSTNAME, self.UDP_PORT))

        # configure the header. Notice that it includes the header
        # information followed by the command 2 (set remote IP)
        # and 0 (no data packets for header).
        packet = struct.pack('4B', 0x55, 0xAA, self.CMD_SET_REMOTE_IP, 0)

        # Sends the packet to the UDP interface, setting the remote IP
        # address of the UDP interface to the host PC
        self.sock.send(packet)

    def recv(self):

        # receive a data packet from the UDP interface
        packet = self.sock.recv(1024)
        if len(packet) < 2:
            return None

        # check that magic number is in first position of packet
        if struct.unpack('>h', packet[:2]) != (0x55AA,):
            print('bad header')
            return None

        # unpack it
        npack = (len(packet)-2) / 4
        if self.recv_type == int:
            fmt = '>%dL' % npack
        elif self.recv_type == float:
            fmt = '>%df' % npack
        result = struct.unpack(fmt, packet[4:])
        
        if self.verbose:
            print('received packet', result)
        
        return result

    def send(self, data=[]):

        if len(data) < 1:
            return None

        if len(data) != self.NPACKETS:
            self.NPACKETS = len(data)

            # configure the header
            self.send_header = struct.pack('4B', 0x55, 0xAA, self.CMD_SEND_DATA, self.NPACKETS)

        # append the 32-bit words to the header
        # '>' in the format string is used to force big-endian
        if self.send_type == int:
            packet = struct.pack(">%di" % self.NPACKETS, *(i for i in data))
        elif self.send_type == float:
            packet = struct.pack(">%df" % self.NPACKETS, *(i for i in data))

        # send the data packet to the UDP interface.
        if self.verbose:
            print('sending packet', data, '...')
        self.sock.send(self.send_header + packet)

if __name__ == '__main__':
    import time

    #host = 'localhost'
    host = '10.10.10.167'
    
    udp = TDTUDP(host=host, send_type=int, recv_type=int)

    # SEND ONLY EXAMPLE
    if 0:
        SEND_PACKETS = 1
        ct = 0
        while 1:
            ct += 1
            fakedata = range(ct % 10, SEND_PACKETS + ct % 10)
            if udp.send_type == float:
                fakedata = [x * 2. for x in fakedata]
            udp.send(fakedata)
            time.sleep(.1) # slow it down a bit

    # RECEIVE ONLY EXAMPLE
    if 0:
        while 1:
            data = udp.recv()
            
            '''
            print('RAW DATA:', end='\t')
            for d in data:
                print(d, end='\t')
            print(8*'\t', end='\r')
            '''
            print(data)
            continue
            # if looking at binner packets, extract sort codes
            unpacked_data = tdt.unpack(data, sort_codes=2, bits_per_bin=4)
            print('UNPACKED DATA:', unpacked_data, end='\t\t\t\r')
            
            # extract a single channel/sort from the unpacked data
            channel = 16
            sort_code = 1
            #print('CHANNEL:', channel, 'SORT:', sort_code, '\t', unpacked_data[sort_code-1][channel-1], end='\t\t\t\r')

    # SEND AND RECEIVE EXAMPLE
    if 1:
        SEND_PACKETS = 8
        ct = 0
        while 1:
            ct += 1
            fakedata = range(ct % 10, SEND_PACKETS + ct % 10)
            if udp.send_type == float:
                fakedata = [x * 2. for x in fakedata]
            
            data = udp.recv()
            print(data)

            udp.send(fakedata)