#!/usr/bin/python
import array
import os
import fcntl
import struct
import threading
import subprocess
from time import time

from can.interfaces.socketcan import SocketcanCtypes_Bus
from can import Message, CanError

BAUDRATES = {
    1000000: 1,
    800000: 2,
    500000: 3,
    250000: 4,
    125000: 5,
    100000: 6,
    50000: 7,
    20000: 8}


def generate_cmd(c, arg=None, cmdlow=None):
    if not arg:
        arg = []
    if not cmdlow:
        cmdlow = len(arg)
    arg[0:0] = [(c << 16) | cmdlow]
    arg += [0] * (64 - len(arg))
    buff = ''
    for i in arg:
        buff += struct.pack('=L', i)
    return buff


def emit(timeout=-1, id=0x601, data=[0x2F, 0x60, 0x60, 0, 1, 0, 0, 0]):
    flags = len(data)
    if id & 0x20000000:
        flags |= 0x40
    msg = struct.pack('=lLLL', timeout, 0, id, flags)
    for i in data:
        msg += struct.pack('=B', i)
    for i in range(8 - len(data)):
        msg += struct.pack('=B', 0)
    return msg


class CMD:
    OPENPORT = 0x01  # Open a CAN channel (no data)
    CLOSEPORT = 0x02  # Close a CAN channel (no data)
    SETBPS = 0x03  # Set bitrate info
    GETBPS = 0x04  # Get bitrate info
    GETVERSION = 0x05  # Get firmware version info
    FIRMWARE = 0x06  # Update card firmware
    FWDATA = 0x07  # Used to pass data during firmware update
    SETPARAM = 0x09  # Set a parameter
    GETPARAM = 0x0A  # Get a parameter
    RECV_THRESH = 0xF9  # Set the receive buffer interrupt threshold
    RECVXMIT = 0xFC  # Receive transmit messages
    DRIVERVER = 0xFE  # Get driver version


class CCERR:
    UNKNOWN_CMD = (0x01, 'Passed command ID was unknown')
    BAD_PARAM = (0x02, 'Illegal parameter passed')
    PORT_OPEN = (0x03, 'Specified CAN port is already open')
    PORT_CLOSED = (0x04, 'Specified CAN port is not open')
    CARD_BUSY = (0x05, 'Card command area is busy')
    INTERNAL = (0x06, 'Some sort of internal device failure')
    TIMEOUT = (0x07, 'Card failed to respond to command')
    SIGNAL = (0x08, 'Signal received by driver')
    MISSING_DATA = (0x09, 'Not enough data was passed')
    CMDMUTEX_HELD = (0x0A, 'The command mutex was being held')
    QUEUECTRL = (0x0B, 'The CAN message queue head/tail was invalid')
    FLASH = (0x0C, 'Failed to erase/program flash memory')
    NOTERASED = (0x0D, 'Attempt to write firmware before erasing flash')
    FLASHFULL = (0x0E, 'Too much data sent when programming flash')
    UNKNOWN_IOCTL = (0x0F, 'Specified IOCTL code was unknown')
    CMD_TOO_SMALL = (0x10, 'Command passed without required header')
    CMD_TOO_BIG = (0x11, 'Command passed with too much data')
    CMD_IN_PROGRESS = (0x12, 'Command already in progress on card')
    CAN_DATA_LENGTH = (0x13, 'More then 8 bytes of data sent with CAN message')
    QUEUE_FULL = (0x14, 'Transmit queue is full')
    QUEUE_EMPTY = (0x15, 'Receive queue is full')
    READ_ONLY = (0x16, 'Parameter is read only')
    MEMORYTEST = (0x17, 'Memory read/write test failure')
    ALLOC = (0x18, 'Memory allocation failure')
    CMDFINISHED = (0x19, 'Used internally by driver')
    DRIVER = (0x1A, 'Generic device driver error')
    CANT_OPEN_PORT = (0x100, 'Unable to obtain handle to device driver')


class IOCTL:
    SENDCAN = 0x4018b704
    RECVCAN = 0xc018b705
    CMD = 0xc008b706


class CmdErr:

    def __init__(self, code):
        if isinstance(code, tuple):
            self.code = code[0]
            self.desc = code[1]
        elif isinstance(code, str):
            self.code = 0xff
            self.desc = code
        else:
            self.code = code
            self.desc = None

    def __str__(self):
        if self.desc is None:
            return 'Error 0x%02x' % self.code
        else:
            return 'Error 0x%02x (%s)' % (self.code, self.desc)


class CanFrame:
    DATA = 0
    RTR = 1
    ERR = 2

    def __init__(self, id=0, data=None):
        self.type = CanFrame.DATA
        self.id = id
        self.data = data
        self.explanation = ""
        self.time = time()
        self.health_check = False
        if self.data is None:
            self.data = []

    def __str__(self):
        s = '0x%08x - ' % self.id
        for i in self.data:
            s += '0x%02x ' % i
        return s


class CanCard(object):

    def __init__(self, fname=None):
        self.isOpen = False
        self.paramlist = ['serial', 'mfgdate', 'pci_volt', '3.3_volt',
                          '2.5_volt', 'canstat', 'options',
                          'chip_date', 'chip_serial', 'password', 'inhibit',
                          'canload', 'boardstatus', 'hwtype']

        self.period = 0.01
        self.transmit_thread = None
        self.stop_event = threading.Event()
        self.syncframe = CanFrame(id=0x80, data=[])
        self.fname = fname
        self.frames_list = []

        # used for frame interpreter
        self.address_map = None
        self.frame = None

        self.copleycancard = True

    @property
    def timeout(self):
        if self.copleycancard:
            return 10
        else:
            return 0.01

    def open(self, baud=1000000):
        # Open a handle to the device driver
        if self.fname is None or self.fname == '':
            if os.path.exists('/dev/eican00'):
                self.fname = '/dev/eican00'
            elif os.path.exists('/dev/copleycan00'):
                self.fname = '/dev/copleycan00'
            else:
                self.copleycancard = False
        else:
            if not os.path.exists(self.fname):
                self.copleycancard = False
        if self.copleycancard:
            self.fd = os.open(self.fname, os.O_RDWR)
            if self.fd < 0:
                raise CmdErr(CCERR.CANT_OPEN_PORT)
            if baud not in BAUDRATES:
                return CmdErr(CCERR.BAD_PARAM)
            # Set the port's baud rate
            self.cmd(CMD.SETBPS, [BAUDRATES[baud]])

            # Open the CAN port
            self.cmd(CMD.OPENPORT)
        else:
            self.channel = "can0"
            self.bring_up_socketcan()
            self.fd = SocketcanCtypes_Bus(channel=self.channel)

        # Close the port if it's already open
        if self.isOpen:
            self.close()

        self.isOpen = True
        return 0

    def bring_up_socketcan(self):
        lsmod_out = subprocess.check_output(['lsmod'])
        if lsmod_out.find("kvaser_usb") == -1:
            subprocess.call('modprobe kvaser_usb', shell=True)
        ip_out = subprocess.check_output(["ip", "link"])
        if ip_out.find(self.channel) == -1:
            raise ValueError("Can interface %s not found." % self.channel)
        else:
            lines = [line for line in ip_out.split("\n")
                     if line.find(self.channel) > -1][0]
            if lines.find("UP") == -1:
                subprocess.call("ip link set can0 up type can bitrate 500000",
                                shell=True)

    def close(self):
        if not self.isOpen:
            return 0

        err = self.cmd(CMD.CLOSEPORT)
        self.isOpen = False
        return err

    def cmd(self, c, arg=None, cmdlow=None):
        if not arg:
            arg = []
        if not cmdlow:
            cmdlow = len(arg)

        arg[0:0] = [(c << 16) | cmdlow]

        arg += [0] * (64 - len(arg))
        buff = b''
        for i in arg:
            buff += struct.pack('=L', i)

        if self.copleycancard:
            buff = fcntl.ioctl(self.fd, IOCTL.CMD, buff)
        else:
            self.fd.send(IOCTL.CMD)

        for i in range(64):
            arg[i] = struct.unpack_from('=L', buff, 4 * i)[0]

        err = (arg[0] >> 16) & 0xffff
        if err:
            raise CmdErr(err)

        l = (arg[0] & 0x3f) + 1
        arg = arg[1:l]

        return arg

    def erase(self, sect='main'):
        codes = {'main': 0x124249AB, 'fpga': 0x35f7091a, 'extend': 0x4C3BC24E,
                 'all': 0x23212321}
        if sect not in codes:
            print('Unknown firmware section')
            return
        self.cmd(CMD.FIRMWARE, [codes[sect]])

    def recv(self, timeout=-1):
        if not self.isOpen:
            raise CmdErr(CCERR.PORT_CLOSED)

        dat = [timeout] + [0] * 5
        buff = b''
        for i in dat:
            buff += struct.pack('=l', i)

        buff = array.array("u", buff)
        frame = CanFrame()

        if self.copleycancard:
            ret = fcntl.ioctl(self.fd, IOCTL.RECVCAN, buff, 1)
            msg = struct.unpack('=lLLLBBBBBBBB', buff)
            if ret:
                return None

            frame.time = msg[1]
            frame.id = msg[2]

            flags = msg[3]
            ct = flags & 0x0F
            for i in range(ct):
                frame.data.append(msg[i + 4])

            if flags & 0x10:
                frame.type = CanFrame.RTR
            else:
                frame.type = CanFrame.DATA

            if flags & 0x40:
                frame.id |= 0x20000000

        else:
            ret = self.fd.recv(timeout=timeout)
            if not ret:
                return ret
            frame.id = ret.arbitration_id
            frame.time = ret.timestamp
            frame.data = ret.data

        self.frames_list.append(frame)
        return frame

    def send_ack(self, frame):
        self.xmit(frame, timeout=self.timeout, append=False)
        while self.recv(timeout=self.timeout) is not None:
            pass

    def xmit(self, frame, timeout=-1, notify=False, append=True):
        frame.data = [i if i else 0 for i in frame.data]
        if not self.isOpen:
            return CmdErr(CCERR.PORT_CLOSED)

        if len(frame.data) > 8:
            return CmdErr(CCERR.BAD_PARAM)

        if self.copleycancard:
            flags = len(frame.data)

            if frame.type == CanFrame.DATA:
                pass
            elif frame.type == CanFrame.RTR:
                flags |= 0x10
            else:
                return CmdErr(CCERR.BAD_PARAM)

            if notify:
                flags |= 0x20

            if frame.id & 0x20000000:
                flags |= 0x40

            msg = struct.pack('=lLLL', timeout, 0, frame.id, flags)

            for i in frame.data:
                msg += struct.pack('=B', i)
            for i in range(8 - len(frame.data)):
                msg += struct.pack('=B', 0)
            if append:
                self.frames_list.append(frame)
            return fcntl.ioctl(self.fd, IOCTL.SENDCAN, msg)
        else:
            msg = Message(arbitration_id=frame.id,
                          data=frame.data,
                          extended_id=False)
            try:
                self.fd.send(msg)
            except CanError:
                self.bring_up_socketcan()
                try:
                    self.fd.send(msg)
                except CanError as e:
                    print(e)
                    pass

    def FindParam(self, param):
        if isinstance(param, int):
            return param
        if param not in self.paramlist:
            raise CmdErr(CCERR.BAD_PARAM)
        return self.paramlist.index(param)

    def get(self, param):
        param = self.FindParam(param)
        return self.cmd(CMD.GETPARAM, [param])[0]

    def set(self, param, value):
        param = self.FindParam(param)
        self.cmd(CMD.SETPARAM, [param, value])

    def reset(self):
        self.cmd(CMD.RESET)
