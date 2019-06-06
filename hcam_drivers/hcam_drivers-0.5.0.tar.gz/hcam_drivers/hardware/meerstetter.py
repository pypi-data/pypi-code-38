# Utility to query and set temps via Ethernet on Meerstetter
from __future__ import absolute_import, unicode_literals, print_function, division
import socket
import random
import six
import struct
from contextlib import contextmanager

from astropy import units as u

# GUI imports
from hcam_widgets.widgets import RangedInt
from hcam_widgets.tkutils import get_root, addStyle
if not six.PY3:
    import Tkinter as tk
else:
    import tkinter as tk


DEFAULT_TIMEOUT = 2

error_codes = {
    '+01': 'Command not available',
    '+02': 'Device is busy',
    '+03': 'Communication error',
    '+04': 'Format error',
    '+05': 'Parameter not available',
    '+06': 'Parameter is read only',
    '+07': 'Value is out of range',
    '+08': 'Instance not available'
}


def hex_to_int(hexstring):
    return int(hexstring, 16)


def hex_to_float32(hexstring):
    if six.PY2:
        byteval = hexstring.decode('hex')
    else:
        byteval = bytes.fromhex(hexstring)
    return struct.unpack(str('!f'), byteval)[0]


def float32_to_hex(f):
    return format(struct.unpack(str('<I'), struct.pack(str('<f'), f))[0], 'X')


class CRCCalculator(object):
    def __init__(self):
        self.polynomial = 0x1021
        self.preset = 0
        self._lut = [self._calc_initial(i) for i in range(256)]

    def _calc_initial(self, c):
        crc = 0
        c = c << 8
        for j in range(8):
            if (crc ^ c) & 0x8000:
                crc = (crc << 1) ^ self.polynomial
            else:
                crc = crc << 1
            c = c << 1
        return crc

    def _update_crc(self, crc, c):
        cc = 0xff & c

        tmp = (crc >> 8) ^ cc
        crc = (crc << 8) ^ self._lut[tmp & 0xff]
        crc = crc & 0xffff
        return crc

    def __call__(self, msg):
        crc = self.preset
        for c in msg:
            crc = self._update_crc(crc, ord(c))
        return format(crc, '0>4X')


@contextmanager
def socketcontext(addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(DEFAULT_TIMEOUT)
        s.connect((addr, port))
        yield s
    finally:
        s.close()


class MeerstetterTEC1090(object):
    """
    Class to use TCP/IP to communicate with TEC-1090 controllers
    mounted in LTR-1200. Communication protocol is MeCom.

    See MeCom protocol spec document 5117B and TEC protocol document
    5136 for details.
    """
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.seq_no = random.randint(1, 1000)
        self.crc_calc = CRCCalculator()
        self.tec_current_limit = 10.7 * u.A

    def _assemble_frame(self, address, payload):
        """
        Assemble the frame of data to send.

        Transmissions are sent in blocks of data known as frames. Each frame has
        several fields:

        1: Control (source); ASCII Char; 1 bytes
        2: Address; UINT8; 2 bytes
        3: Sequence No; UINT16; 4 bytes
        4: Payload; N bytes
        5: Checksum, 4 bytes
        6: End of Frame, 1 byte <CR>
        """
        cs = '#'
        addr = format(address, '0>2X')
        seq = format(self.seq_no, '0>4X')
        self.seq_no += 1
        msg = cs + addr + seq + payload
        eof = '\r'
        return msg + self.crc_calc(msg) + eof

    def _send_frame(self, frame_msg):
        with socketcontext(self.address, self.port) as s:
            welcome = s.recv(1024)
            if 'Welcome' not in welcome.decode():
                raise IOError('did not receive welcome message from meerstetter')
            s.send(frame_msg.encode())
            ret_msg = s.recv(1024)
        ret_msg = ret_msg.decode().strip()
        self._check_response(frame_msg, ret_msg)
        return self._strip_response(ret_msg)

    def _check_response(self, frame_msg, ret_msg):
        if ret_msg[0] == '!' and frame_msg[1:7] == ret_msg[1:7]:
            # a valid response, and same seq no. so far so good
            crc_back = ret_msg[-4:]
            crc_out = frame_msg[-5:-1]
            package_in = ret_msg[:-4]
            if self.crc_calc(package_in) != crc_back and crc_out != crc_back:
                raise IOError('checksum of return message not OK:\nOut: {}\nBack: {}'.format(
                                frame_msg, ret_msg
                              ))
        else:
            raise IOError('response not from device, or sequence number mismatch:\nOut: {}\nBack: {}'.format(
                            frame_msg, ret_msg
                          ))

    def _strip_response(self, ret_msg):
        return ret_msg[7:-4]

    def get_param(self, address, param_no, instance, param_type='float'):
        payload = '?VR{param_no:0>4X}{instance:0>2X}'.format(
            param_no=param_no, instance=instance
        )
        frame_msg = self._assemble_frame(address, payload)
        encoded_param_val = self._send_frame(frame_msg)
        if encoded_param_val == '+05':
            raise IOError('param {} not available'.format(param_no))

        if param_type == 'float':
            return hex_to_float32(encoded_param_val)
        else:
            return hex_to_int(encoded_param_val)

    def reset_tec(self, address):
        payload = 'RS'
        frame_msg = self._assemble_frame(address, payload)
        ret_msg = self._send_frame(frame_msg)
        if ret_msg != '':
            raise IOError('unexpected response to reset command {}'.format(ret_msg))

    def set_ccd_temp(self, address, target_temp):
        param_no = 3000
        payload = 'VS{param_no:0>4X}{instance:0>2X}{encoded_val}'.format(
            param_no=param_no, instance=1,
            encoded_val=float32_to_hex(target_temp)
        )
        frame_msg = self._assemble_frame(address, payload)
        ret_msg = self._send_frame(frame_msg)
        if ret_msg.startswith('+'):
            if ret_msg in error_codes:
                raise IOError(error_codes[ret_msg])
            else:
                raise IOError('unknown error code {}'.format(ret_msg))

    def get_ccd_temp(self, address):
        param_no = 1000
        return self.get_param(address, param_no, 1)*u.Celsius

    def get_setpoint(self, address):
        param_no = 1010
        return self.get_param(address, param_no, 1)*u.Celsius

    def get_heatsink_temp(self, address):
        param_no = 1001
        return self.get_param(address, param_no, 1)*u.Celsius

    def get_power(self, address):
        current = self.get_param(address, 1020, 1)
        voltage = self.get_param(address, 1021, 1)
        return current*voltage*u.W

    def get_current(self, address):
        return self.get_param(address, 1020, 1) * u.A

    def get_status(self, address):
        param_no = 104
        status = self.get_param(address, param_no, 1, param_type='int')
        lut = {0: 'init', 1: 'ready', 2: 'run', 3: 'error',
               4: 'bootloader', 5: 'resetting'}
        # return OK/NOK and status
        return status <= 2, lut[status]


class CCDTempFrame(tk.LabelFrame):
    """
    Self-contained widget to control CCD temps and reset TECS.
    """
    def __init__(self, master):
        tk.LabelFrame.__init__(
            self, master, text='CCD TECs', padx=10, pady=4
        )
        # Top for table of buttons
        top = tk.Frame(self)
        g = get_root(self).globals

        self.meerstetters = [
            MeerstetterTEC1090(ip_addr, 50000) for ip_addr in
            g.cpars['meerstetter_ip']
        ]
        ms1 = self.meerstetters[0]
        ms2 = self.meerstetters[1]
        self.ms_mapping = {1: (ms1, 1), 2: (ms1, 2), 3: (ms1, 3),
                           4: (ms2, 1), 5: (ms2, 2)}

        tk.Label(top, text='CCD1').grid(row=0, column=0)
        tk.Label(top, text='CCD2').grid(row=0, column=1)
        tk.Label(top, text='CCD3').grid(row=0, column=2)
        tk.Label(top, text='CCD4').grid(row=0, column=3)
        tk.Label(top, text='CCD5').grid(row=0, column=4)

        self.temp_entry_widgets = {}
        self.setpoint_displays = {}
        self.reset_buttons = {}
        width = 8
        for i in range(1, 6):
            ms, address = self.ms_mapping[i]
            try:
                ival = ms.get_setpoint(address).value
            except:
                ival = 5
            self.temp_entry_widgets[i] = RangedInt(
                top, ival, -100, 20, None, True, width=width
            )
            self.temp_entry_widgets[i].grid(row=1, column=i-1)
            self.setpoint_displays[i] = tk.Label(top, text='nan', width=width)
            self.setpoint_displays[i].grid(row=2, column=i-1)
            self.reset_buttons[i] = tk.Button(
                top, fg='black', width=width, text='Reset',
                command=lambda ccd=i: self.reset(ccd))
            self.reset_buttons[i].grid(row=3, column=i-1)

        # bind enter to set value routine
        for i in range(1, 6):
            widget = self.temp_entry_widgets[i]
            widget.unbind('<Return>')
            widget.bind('<Return>', lambda event, ccd=i: self.update(ccd))

        top.pack(pady=2)
        addStyle(self)
        self.refresh_setpoints()

    def update(self, ccd):
        g = get_root(self).globals
        if not g.cpars['ccd_temp_monitoring_on']:
            g.clog.warn('Temperature monitoring disabled. Will not update CCD{}'.format(ccd))
            return
        g.clog.info('Updating CCD{}'.format(ccd))
        widget = self.temp_entry_widgets[ccd]
        val = widget.value()
        g.clog.info('desired setpoint ' + str(val))
        ms, address = self.ms_mapping[ccd]
        try:
            ms.set_ccd_temp(address, int(val))
            self.after(500, self.refresh_setpoints)
        except:
            g.clog.warn('Unable to update setpoint for CCD{}'.format(ccd))

    def reset(self, ccd):
        g = get_root(self).globals
        if not g.cpars['ccd_temp_monitoring_on']:
            g.clog.warn('Temperature monitoring disabled. Will not reset CCD{}'.format(ccd))
            return
        g.clog.info('Resetting TEC {}'.format(ccd))
        ms, address = self.ms_mapping[ccd]
        try:
            ms.reset_tec(address)
        except:
            g.clog.warn('Unable to reset TEC {}'.format(ccd))

    def refresh_setpoints(self):
        g = get_root(self).globals
        if not g.cpars['ccd_temp_monitoring_on']:
            g.clog.warn('Temperature monitoring disabled. Cannot refresh CCD setpoints')
            return
        for i in range(1, 6):
            widget = self.setpoint_displays[i]
            ms, address = self.ms_mapping[i]
            try:
                setpoint = ms.get_setpoint(address).value
            except:
                g.clog.warn('Unable to get setpoint for CCD{}'.format(i))
            widget.configure(text=str(setpoint))
