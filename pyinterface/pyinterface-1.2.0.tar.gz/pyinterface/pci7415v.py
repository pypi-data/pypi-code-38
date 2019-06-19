
import struct
import time
from . import core

# functions
# =========

def to_prmv_format(x):
    data = []
    for i in range(len(x)):
        a = int(x[i]) & 0xfffffff
        data.append(struct.pack('<I', a))
    return data

def to_prfl_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prfh_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prur_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prdr_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prmg_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prdp_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prmd_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prip_format(x):
    data = []
    for i in range(len(x)):
        a = x[i] & 0xfffffff
        data.append(struct.pack('<I', a))
    return data

def to_prus_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def to_prds_format(x):
    data = []
    for i in range(len(x)):
        a = x[i]
        data.append(struct.pack('<I', a))
    return data

def from_prmv_format(x):
    data = []
    for i in range(len(x)):
        a = x[i].to_bit()
        b = a[0:28][::-1]
        c = -int(b[0]) << len(b) | int(b, 2)
        data.append(c)
    return data

def from_rpls_format(x):
    data = []
    for i in range(len(x)):
        a = x[i].to_bit()
        b = a[0:28][::-1]
        c = -int(b[0]) << len(b) | int(b, 2)
        data.append(c)
    return data

def do_nothing(x):
    return x

class pci7415v_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('TD1', 'TD2', 'TD3', 'TD4', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('DI1', 'DI2', 'DI3', 'DI4', 'DI5', 'DI6', 'DI7', 'DI8'),
            ('DI9', 'DI10', 'DI11', 'DI12', '', '', '', ''),
            ('ELL1', 'ELL2', 'ELL3', 'ELL4', '', '', '', ''),
            ('SIGC', 'SIGT', 'SIGR', 'SIGI', '', '', '', ''),
            ('', 'MIRT', 'MIRR', 'MIRI', '', '', '', ''),
            ('LOCK', 'EXTRST', 'LOCKRST', '', '', '', '', ''),
            ('CLKMODE0', 'CLKMODE1', '', '', '', '', '', ''),
            ('AUTOBUSY', 'STEPBUSY', 'STEPMODE', '', 'ROMBUSY', '', '', ''),
            ('ND0', 'ND1', 'ND2', 'ND3', 'ND4', 'ND5', 'ND6', 'ND7'),
            ('ND8', 'ND9', 'ND10', 'ND11', '', '', '', ''),
            ('ED0', 'ED1', 'ED2', 'ED3', 'ED4', 'ED5', 'ED6', 'ED7'),
            ('ED8', 'ED9', 'ED10', 'ED11', '', '', '', ''),
            ('SYNCLINE0', 'SYNCLINE1', 'SYNCLINE2', '', 'SIGSEL', '', '', 'RD'),
            ('BID0', 'BID1', 'BID2', 'BID3', '', '', '', '')
        ),
        (
            ('SSCM', 'SRUN', 'SENI', 'SEND', 'SERR', 'SINT', 'SSC0', 'SSC1'),
            ('SCP1', 'SCP2', 'SCP3', 'SCP4', 'SCP5', 'SEOR', 'SPRF', 'SPDF'),
            ('IOP0', 'IOP1', 'IOP2', 'IOP3', 'IOP4', 'IOP5', 'IOP6', 'IOP7'),
            ('SFU', 'SFD', 'SFC', 'SALM', 'SPEL', 'SMEL', 'SORG', 'SSD'),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('SSCM', 'SRUN', 'SENI', 'SEND', 'SERR', 'SINT', 'SSC0', 'SSC1'),
            ('SCP1', 'SCP2', 'SCP3', 'SCP4', 'SCP5', 'SEOR', 'SPRF', 'SPDF'),
            ('IOP0', 'IOP1', 'IOP2', 'IOP3', 'IOP4', 'IOP5', 'IOP6', 'IOP7'),
            ('SFU', 'SFD', 'SFC', 'SALM', 'SPEL', 'SMEL', 'SORG', 'SSD'),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('SSCM', 'SRUN', 'SENI', 'SEND', 'SERR', 'SINT', 'SSC0', 'SSC1'),
            ('SCP1', 'SCP2', 'SCP3', 'SCP4', 'SCP5', 'SEOR', 'SPRF', 'SPDF'),
            ('IOP0', 'IOP1', 'IOP2', 'IOP3', 'IOP4', 'IOP5', 'IOP6', 'IOP7'),
            ('SFU', 'SFD', 'SFC', 'SALM', 'SPEL', 'SMEL', 'SORG', 'SSD'),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('SSCM', 'SRUN', 'SENI', 'SEND', 'SERR', 'SINT', 'SSC0', 'SSC1'),
            ('SCP1', 'SCP2', 'SCP3', 'SCP4', 'SCP5', 'SEOR', 'SPRF', 'SPDF'),
            ('IOP0', 'IOP1', 'IOP2', 'IOP3', 'IOP4', 'IOP5', 'IOP6', 'IOP7'),
            ('SFU', 'SFD', 'SFC', 'SALM', 'SPEL', 'SMEL', 'SORG', 'SSD'),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37')
        )
    )

    bit_flags_out = (
        (
            ('TCTRL1', 'TCTRL2', 'TCTRL3', 'TCTRL4', 'SCK1' ,'SCK2' ,'SCK3' ,''),
            ('', '', '', '', '', '', '', ''),
            ('DO1', 'DO2', 'DO3', 'DO4', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('ELL1', 'ELL2', 'EL3', 'ELL4', '', '', '', ''),
            ('SIGRCLR1', 'SIGRCLR2', 'SIGRCLR3', 'SIGRCLR4', 'SIGICLR1', 'SIGICLR2', 'SIGICLR3', 'SIGICLR4'),
            ('', 'MIRT', 'MIRR', 'MIRI', '', '', '', ''),
            ('', 'EXTRST', 'LOCKRST', '', '', '', '', ''),
            ('CLKMODE0', 'CLKMODE1', 'CSTAOUT', 'CSTPOUT', '', '', '', ''),
            ('AUTO', 'STEP', 'STEPMODE', '', '', '', '', ''),
            ('ND0', 'ND1', 'ND2', 'ND3', 'ND4', 'ND5', 'ND6', 'ND7'),
            ('ND8', 'ND9', 'ND10', 'ND11', '', '', '', ''),
            ('ED0', 'ED1', 'ED2', 'ED3', 'ED4', 'ED5', 'ED6', 'ED7'),
            ('ED8', 'ED9', 'ED10', 'ED11', '', '', '', ''),
            ('SYNCLINE0', 'SYNCLINE1', 'SYNCLINE2', '', 'SIGSEL', '', '', 'RD'),
            ('', '', '', '', '', '', '', '')
        ),
        (
            ('COMB00', 'COMB01', 'COMB02', 'COMB03', 'COMB04', 'COMB05', 'COMB06', 'COMB07'),
            ('SELx', 'SELy', 'SELz', 'SELu', '', '', '', ''),
            ('OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5', 'OTP6', 'OTP7'),
            ('', '', '', '', '', '', '', ''),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('COMB00', 'COMB01', 'COMB02', 'COMB03', 'COMB04', 'COMB05', 'COMB06', 'COMB07'),
            ('SELx', 'SELy', 'SELz', 'SELu', '', '', '', ''),
            ('OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5', 'OTP6', 'OTP7'),
            ('', '', '', '', '', '', '', ''),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('COMB00', 'COMB01', 'COMB02', 'COMB03', 'COMB04', 'COMB05', 'COMB06', 'COMB07'),
            ('SELx', 'SELy', 'SELz', 'SELu', '', '', '', ''),
            ('OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5', 'OTP6', 'OTP7'),
            ('', '', '', '', '', '', '', ''),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37'),
            ('COMB00', 'COMB01', 'COMB02', 'COMB03', 'COMB04', 'COMB05', 'COMB06', 'COMB07'),
            ('SELx', 'SELy', 'SELz', 'SELu', '', '', '', ''),
            ('OTP0', 'OTP1', 'OTP2', 'OTP3', 'OTP4', 'OTP5', 'OTP6', 'OTP7'),
            ('', '', '', '', '', '', '', ''),
            ('BUFB00', 'BUFB01', 'BUFB02', 'BUFB03', 'BUFB04', 'BUFB05', 'BUFB06', 'BUFB07'),
            ('BUFB10', 'BUFB11', 'BUFB12', 'BUFB13', 'BUFB14', 'BUFB15', 'BUFB16', 'BUFB17'),
            ('BUFB20', 'BUFB21', 'BUFB22', 'BUFB23', 'BUFB24', 'BUFB25', 'BUFB26', 'BUFB27'),
            ('BUFB30', 'BUFB31', 'BUFB32', 'BUFB33', 'BUFB34', 'BUFB35', 'BUFB36', 'BUFB37')
        )
    )

    cmd_dic = {
        'write': {
            'prmv': {'cmd': 0x80, 'func': to_prmv_format},
            'prfl': {'cmd': 0x81, 'func': to_prfl_format},
            'prfh': {'cmd': 0x82, 'func': to_prfh_format},
            'prur': {'cmd': 0x83, 'func': to_prur_format},
            'prdr': {'cmd': 0x84, 'func': to_prdr_format},
            'prmg': {'cmd': 0x85, 'func': to_prmg_format},
            'prdp': {'cmd': 0x86, 'func': to_prdp_format},
            'prmd': {'cmd': 0x87, 'func': to_prmd_format},
            'prip': {'cmd': 0x88, 'func': to_prip_format},
            'prus': {'cmd': 0x89, 'func': to_prus_format},
            'prds': {'cmd': 0x8A, 'func': to_prds_format}
        },
        'read': {
            'prmv': {'cmd': 0xC0, 'func': from_prmv_format},
            'prfl': {'cmd': 0xC1},
            'prfh': {'cmd': 0xC2},
            'pruh': {'cmd': 0xC3},
            'prdr': {'cmd': 0xC4},
            'prmg': {'cmd': 0xC5},
            'prdp': {'cmd': 0xC6},
            'prmd': {'cmd': 0xC7},
            'prip': {'cmd': 0xC8},
            'prus': {'cmd': 0xC9},
            'prds': {'cmd': 0xCA},
            'rsts': {'cmd': 0xF1, 'func': do_nothing},
            'rpls': {'cmd': 0xF4, 'func': from_rpls_format}
        },
        'send': {
            'fchgl': {'cmd': 0x40}, 'fchgh': {'cmd': 0x41},
            'fschl': {'cmd': 0x42}, 'fschh': {'cmd': 0x43},
            'stop': {'cmd': 0x49}, 'sdstp': {'cmd': 0x4a},
            'stafl': {'cmd': 0x50}, 'stafh': {'cmd': 0x51},
            'stad': {'cmd': 0x52}, 'staud': {'cmd': 0x53},
            'cntfl': {'cmd': 0x54}, 'cntfh': {'cmd': 0x55},
            'cntd': {'cmd': 0x56}, 'cntud': {'cmd': 0x57},
            'srst': {'cmd': 0x04}
        }
    }

    mode_dic = {'PTP': 0x41, 'JOG':0x00}

    do_flag = {1: 0, 2: 0, 3: 0 , 4: 0}
    do_mapper = {'x': 1, 'y': 2, 'z': 3}
    move_mode = {'x': '', 'y': '', 'z': '', 'u': ''}

    def get_board_id(self):
        bar = 0
        offset = 0x0F
        size = 1
        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]
        return bid

    def get_main_status(self, axis):
        bar = 1
        offset = 0x00
        offset_li = self._make_offset_list(offset, axis)
        size = 2
        status_li = []
        for i in range(len(axis)):
            status = self.read(bar, offset_li[i], size)
            status_li.append(status.to_bit())
            time.sleep(0.01)
        return status_li

    def _select_axis_for_command(self, axis):
        axis_num = 0b00000000
        axis_dic = {'x': 0b00000001, 'X': 0b00000001,
                    'y': 0b00000010, 'Y': 0b00000010,
                    'z': 0b00000100, 'Z': 0b00000100,
                    'u': 0b00001000, 'U': 0b00001000}
        for i in range(len(axis)):
            axis_num |= axis_dic[axis[i]]
        return axis_num

    def _make_offset_list(self, offset, axis):
        axis_dic = {'x': 0x00, 'y': 0x08, 'z': 0x10, 'u': 0x18,
                    'X': 0x00, 'Y': 0x08, 'Z': 0x10, 'U': 0x18}
        axis_li = []
        for i in range(len(axis)):
            axis_li.append(offset + axis_dic[axis[i]])
        return axis_li

    def pcl_write_command(self, cmd, axis):
        bar = 1
        offset = 0x00
        axis_num = self._select_axis_for_command(axis)
        cmd = cmd.to_bytes(1, 'little')
        axis_num = axis_num.to_bytes(1, 'little')
        cmdaxis = cmd + axis_num
        self.write(bar, offset, cmdaxis)
        time.sleep(0.01)
        return

    def pcl_write_data(self, data, axis):
        bar = 1
        offset = 0x04
        offset_li = self._make_offset_list(offset, axis)
        for i in range(len(axis)):
            self.write(bar, offset_li[i], data[i])
            time.sleep(0.01)
        return

    def pcl_read_data(self, axis):
        bar = 1
        offset = 0x04
        offset_li = self._make_offset_list(offset, axis)
        size = 4
        data_li = []
        for i in range(len(axis)):
            data_li.append(self.read(bar, offset_li[i], size))
            time.sleep(0.01)
        return data_li

    def set_param(self, data, name, axis):
        comb0 = self.cmd_dic['write'][name]['cmd']
        data = self.cmd_dic['write'][name]['func'](data)
        self.pcl_write_data(data, axis)
        self.pcl_write_command(comb0, axis)
        return

    def get_param(self, name, axis):
        comb0 = self.cmd_dic['read'][name]['cmd']
        self.pcl_write_command(comb0, axis)
        data_flag = self.pcl_read_data(axis)
        data = self.cmd_dic['read'][name]['func'](data_flag)
        return data

    def send_cmd(self, name, axis):
        comb0 = self.cmd_dic['send'][name]['cmd']
        self.pcl_write_command(comb0, axis)
        return

    def _input_di(self, axis):
        pass

    def _output_do(self, do_num, onoff):
        bar = 0
        offset = 0x02
        self.do_dic[do_num] = onoff
        do_str = ''
        for i in self.do_dic:
            do_str = str(self.do_dic[i]) + do_str
        do_int = int(do_str, 2)
        do_byte = struct.pack('<H', do_int)
        self.write(bar, offset, do_byte)
        return

###=== temp ===

    def initializer(self, axis='xyzu', mode=['JOG', 'JOG', 'JOG', 'JOG']):
        self.send_cmd(name='srst', axis=axis)
        time.sleep(0.1)
        self.pcl_init(axis=axis)
        self.set_mode(mode=mode, axis=axis)
        return

    def finalizer(self, axis='xyzu'):
        self.send_cmd(name='srst', axis=axis)
        time.sleep(0.1)
        return

    def pcl_init(self, axis):
        self.set_param(name='prmv', data=[100, 100, 100, 100], axis=axis)
        self.set_param(name='prfl', data=[100, 100, 100, 100], axis=axis)
        self.set_param(name='prfh', data=[1000, 1000, 1000, 1000], axis=axis)
        self.set_param(name='prur', data=[1000, 1000, 1000, 1000], axis=axis)
        self.set_param(name='prdr', data=[1000, 1000, 1000, 1000], axis=axis)
        self.set_param(name='prmg', data=[2999, 2999, 2999, 2999], axis=axis)
        self.set_param(name='prdp', data=[0, 0, 0, 0], axis=axis)
        self.set_param(name='prip', data=[0, 0, 0, 0], axis=axis)
        self.set_param(name='prus', data=[0, 0, 0, 0], axis=axis)
        self.set_param(name='prds', data=[0, 0, 0, 0], axis=axis)
        return

    def move(self, axis, move_cmd='stafh', check_onoff=False):
        if check_onoff == False:
            self.send_cmd(name=move_cmd, axis=axis)
        if check_onoff == True:
            off_axis = self._get_onoff_axis(axis=axis, onoff=0)
            if off_axis == '': pass
            else: self.send_cmd(name=move_cmd, axis=off_axis)
        return

    def stop(self, axis, stop_cmd='stop', check_onoff=False):
        if check_onoff == False:
            self.send_cmd(name=stop_cmd, axis=axis)
        if check_onoff == True:
            on_axis = self._get_onoff_axis(axis=axis, onoff=1)
            if on_axis == '': pass
            else: self.send_cmd('stop', axis=on_axis)
        return

    def set_mode(self, mode, axis):
        self.stop(axis=axis, check_onoff=True)
        data = []
        for i in range(len(axis)):
            data.append(self.mode_dic[mode[i]])
            self.move_mode[axis[i]] = mode[i]
        self.set_param(name='prmd', data=data, axis=axis)
        return

    def set_length(self, length, axis):
        # for Nagoya: unit = mm
        data_li = []
        for i in range(len(axis)):
            data_li.append(length[i]*100)
        self.set_param(data=data_li, name='prmv', axis=axis)
        return

    def get_length(self, axis):
        # for Nagoya: unit = mm
        data = self.get_param(name='prmv', axis=axis)
        for i in range(len(data)):
            data[i] = data[i]/100
        return data

    def set_speed(self, speed, axis):
        pass

    def get_speed(self, axis):
        pass

    def set_position(self, position, axis):
        # for Nagoya: unit = mm
        pass

    def get_position(self, axis):
        # for Nagoya: unit = mm
        pass

    def move_to_home(self, axis):
        # for Nagoya: axis is 'x' or 'y' or 'z'
        self.stop(axis=axis, check_onoff=True)
        for i in axis:
            self._output_do(do_num=self.do_mapper[i], onoff=1)
        time.sleep(1)
        for i in axis:
            self._output_do(do_num=self.do_mapper[i], onoff=0)
        return

    def check_move_onoff(self, axis):
        status_li = self.get_main_status(axis=axis)
        move_onoff_list = []
        for i in range(len(axis)):
            move_onoff_list.append(int(status_li[i][0]))
        return move_onoff_list

    def get_operate_condition(self, axis):
        data = self._get_extended_status(axis)
        for i in range(len(data)):
            data[i] = data[i][0:4][::-1]
        return data

    def get_residual_pulse(self, axis):
        data = self.get_param(name='rpls', axis=axis)
        return data

    def _get_onoff_axis(self, axis, onoff):
        _onoff = self.check_move_onoff(axis=axis)
        onoff_axis = ''
        for i in range(len(axis)):
            if _onoff[i] == onoff: onoff_axis = onoff_axis + axis[i]
            else: pass
        return onoff_axis

    def _get_extended_status(self, axis):
        data = self.get_param(name='rsts', axis=axis)
        for i in range(len(axis)):
            data[i] = data[i].to_bit()
        return data
