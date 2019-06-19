
import struct
import pypci


# functions
# ---------

def bytes2bit(bytes_data):
    return ''.join([format(byte, '08b')[::-1] for byte in bytes_data])

def bit2bytes(bit_str):
    bit_str += ('0' * ((8 - len(bit_str)) % 8))
    d = b''
    for i in range(int(len(bit_str)/8)):
        bb = bit_str[8*i:8*(i+1)]
        d += int(bb[::-1], 2).to_bytes(1, 'little')
        continue
    return  d

def bytes2list(bytes_data):
    return list(map(int, bytes2bit(bytes_data)))

def list2bytes(bit_list):
    bit_str = ''.join(map(str, bit_list))
    return bit2bytes(bit_str)


# class
# -----

class interface_driver(object):
    config = None
    board_id = -1
    
    bar = []
    bit_flags_in = ()
    bit_flags_out = ()
    log_bytes_in = []
    log_bytes_out = []
    
    def __init__(self, pci_config):
        self.config = pci_config
        self.bar = pci_config.bar
        self.log_bytes_in = [bytearray(bytes(_.size)) for _ in self.bar]
        self.log_bytes_out = [bytearray(bytes(_.size)) for _ in self.bar]
        self.board_id = self.get_board_id()
        pass
    
    def read(self, bar_num, offset, size):
        bar = self.bar[bar_num]
        ret = pypci.read(bar, offset, size)
        self.log_bytes_in[bar_num][offset:offset+size] = ret
        flag = self.bit_flags_in[bar_num][offset:offset+size]
        fb = flagged_bytes(ret, flag)
        return fb
    
    def write(self, bar_num, offset, data):
        size = len(data)
        bar = self.bar[bar_num]
        pypci.write(bar, offset, data)
        self.log_bytes_out[bar_num][offset:offset+size] = data
        return
    
    def set_flag(self, bar_num, offset, flag):
        bar = self.bar[bar_num]
        flag_list = self.bit_flags_out[bar_num][offset]
        flags = flag.split()
        
        bit = ''
        for f in flag_list:
            if f in flags:
                bit += '1'
            else:
                bit += '0'
                pass
            continue
        
        d = bit2bytes(bit)
        self.write(bar_num, offset, d)
        return
    
    def get_log(self, in_out, bar_num, offset):
        if in_out == 'in':
            d = self.log_bytes_in[bar_num][offset:offset+1]
            f = self.bit_flags_in[bar_num][offset:offset+1]
            
        elif in_out == 'out':            
            d = self.log_bytes_out[bar_num][offset:offset+1]
            f = self.bit_flags_out[bar_num][offset:offset+1]
        
        else:
            return
            
        return flagged_bytes(d, f)
    
    
    def get_board_id(self):
        pass





class flagged_bytes(object):
    bytes = b''
    bit_flag = ()
    fmt = ''
    
    def __init__(self, bytes, bit_flag=(), fmt=''):
        self.bytes = bytes
        
        if bit_flag != ():
            self.bit_flag = bit_flag
            pass
            
        if fmt != '':
            self.fmt = fmt
            pass
        
        pass
        
    def __repr__(self):
        return '<flagged_bytes size={0} bytes=0x{1}>'.format(len(self.bytes),
                                                             self.to_hex())
    
    def __getitem__(self, key):
        if isinstance(key, str):
            dictlist = self.to_dictlist()
            for item in self.to_dictlist():
                if item['flag'] == key: 
                    return item['value']
                continue
            return None
        
        bit = self.to_list()
        return bit[key]
        
    def set_flag(self, flag):
        self.bit_flag = flag
        return
        
    def set_fmt(self, fmt):
        self.fmt = fmt
        return
    
    def to_hex(self):
        return self.bytes.hex()
        
    def to_bit(self):
        return bytes2bit(self.bytes)
        
    def to_list(self):
        return bytes2list(self.bytes)
        
    def to_dictlist(self):
        bit = self.to_list()
        flag_list = [f for flags in self.bit_flag for f in flags]
        dictlist = [{'index': i, 'flag': f, 'value': b} for i, (b, f)
                    in enumerate(zip(bit, flag_list))]
        return dictlist
        
    def to_int(self):
        if len(self.bytes) == 1:
            return self.unpack('<b')
        
        if len(self.bytes) == 2:
            return self.unpack('<h')
        
        if len(self.bytes) == 4:
            return self.unpack('<i')

        if len(self.bytes) == 8:
            return self.unpack('<q')
        
        return 0
    
    def to_uint(self):
        if len(self.bytes) == 1:
            return self.unpack('<B')
        
        if len(self.bytes) == 2:
            return self.unpack('<H')
        
        if len(self.bytes) == 4:
            return self.unpack('<I')

        if len(self.bytes) == 8:
            return self.unpack('<Q')
        
        return 0
    
    def to_float(self):
        if len(self.bytes) == 2:
            return self.unpack('<e')
        
        if len(self.bytes) == 4:
            return self.unpack('<f')

        if len(self.bytes) == 8:
            return self.unpack('<d')
        
        return 0.0
        
    def to_flags(self):
        dictlist = self.to_dictlist()
        flag = ' '.join([item['flag'] for item in dictlist 
                         if item['value']==1])
        return flag

    def unpack(self, fmt=''):
        if fmt == '': fmt = self.fmt
        ret = struct.unpack(fmt, self.bytes)
        if len(ret) == 1: ret = ret[0]
        return ret

    def print(self):
        msg = '%s\n\n'%(object.__repr__(self))
        
        for i, byte in enumerate(self.bytes):
            bits1 = format(byte, '08b')
            bits2 = bits1[::-1]
            msg += 'value = 0x{byte:02X} (0b{bits1})\n'.format(**locals())
            for j, (bit, name) in enumerate(zip(bits2, self.bit_flag[i])):
                if name == '':
                    msg += '  {j} : {bit}\n'.format(**locals())
                else:
                    msg += '  {j} : {name} = {bit}\n'.format(**locals())
                    pass
                continue
            msg += '\n'
            continue
        
        print(msg)
        return
    
