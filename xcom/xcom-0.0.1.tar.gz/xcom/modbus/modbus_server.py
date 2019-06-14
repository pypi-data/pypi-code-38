import logging

from .modbus import *
from .modbus_sepam_opg import Sepam, SepamType
from ..tools import *


def _mb_create_header_as_bytearray(tid, rtulen, slaveNb, fnNb) -> bytearray:
    return bytearray([hi(tid), lo(tid), 0, 0, hi(rtulen), lo(rtulen), slaveNb, fnNb])


def _mb_create_exc(tid, slaveNb, fnNb, excNb) -> bytearray:
    resp = _mb_create_header_as_bytearray (tid, 3, slaveNb, fnNb | 0x80)
    resp.append(excNb)
    return resp


SEPAM_TYPES = {
    's80': SepamType.S80,
    's40': SepamType.S40,
    's20': SepamType.S20,
    's2k': SepamType.S2K,
}

class MbProtocol:
    DefaultPort = 502
    Slaves = {}

    def __init__(self):
        self.log = logging.getLogger('modbus')
        self.log.info ('Create Modbus server')

        self.Enabled = True
        self.RcvBuf = []

    # получает на вход конец (remainder) командной строки с перечнем устройств
    def parse_config(devices, log):
        for dev in devices:
            tokens = dev.split(',')
            type_str = tokens[0]
            dev_type = SEPAM_TYPES.get(type_str)
            if not dev_type:
                raise UserWarning(f'Invalid device type: "{type_str}". Available: {list(SEPAM_TYPES.keys())}')

            try:
                slave_nb = 1 if len(tokens) < 2 else int(tokens[1])
            except ValueError:
                raise UserWarning(f'Invalid device slave nb: "{tokens[1]}" for "{dev}". Should be integer')

            if slave_nb < 0 or slave_nb > 255 or slave_nb in MbProtocol.Slaves:
                raise UserWarning(f'Invalid or duplicated slave nb {slave_nb} for "{dev}"')
            
            MbProtocol.Slaves[slave_nb] = Sepam(dev_type, log)
            
        if not MbProtocol.Slaves:
            raise UserWarning('No devices configured')

    # returns sequence of bytes or ExceptionNumber if connection is to be closed
    def get_response(self, data) -> (bytes, bytearray, int, None):
        
        log = self.log
    
        nbAllBytes = len(data)
        if nbAllBytes < 6:
            return None    # wait more data
            
        tid = word (data[0], data[1])
        rtulen = word(data[4], data[5])
        
        if nbAllBytes < (rtulen+6):
            return None    # wait more data
            
        rtu = data[6:6 + rtulen]
        slaveNb = rtu[0]
        fnNb = rtu[1]

        if fnNb==1 or fnNb==2:    # read bits
            if rtulen!=6:
                raise Exception ("For fn1, fn2 rtulen should be 6, not {}".format(rtulen))
                
            if slaveNb not in MbProtocol.Slaves:
                return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
            
            slave = MbProtocol.Slaves[slaveNb]
            
            addr = word(rtu[2], rtu[3])
            nb = word(rtu[4], rtu[5])
            
            data = slave.ReadOutBits (addr, nb) if fnNb==1 else slave.ReadInBits (addr, nb)
            if type(data) is int:
                return _mb_create_exc(tid, slaveNb, fnNb, int(data))
            else:
                return MbProtocol.CreateReadBitsReply(tid, slaveNb, fnNb, data)
            
        elif fnNb==3 or fnNb==4:    # read words
            addr = None
            nb = None
            try:
                if rtulen!=6:
                    raise UserWarning (f'Rtu should be 6 bytes, not {rtulen}')
                    
                slave = MbProtocol.Slaves.get(slaveNb)
                if not slave:
                    return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
                
                addr = word(rtu[2], rtu[3])
                nb = word(rtu[4], rtu[5])
                
                if nb > MB_MAX_READ_WORDS_NB:
                    log.warning('Modbus exceeds data size: %s', nb)
                    return _mb_create_exc(tid, slaveNb, fnNb, EXC_ILLEGAL_DATA_ADDRESS)

                log.debug(f'{FN_NAMES[fnNb]} [slave={slaveNb} addr={addr} nb={nb}]')
                
                try:
                    data = slave.ReadOutWords(addr, nb) if fnNb==3 else slave.ReadInWords (addr, nb)
                except ModbusException as ex:
                    log.warning(f'{FN_NAMES[fnNb]} [addr={addr} nb={nb}]: {ex}')
                    return _mb_create_exc(tid, slaveNb, fnNb, ex.exc_code)
                    
                # Exception?
                if isinstance(data, int):
                    log.warning(f'Modbus exception {data}: {EXC_NAMES.get(data, "unknown")}')
                    return _mb_create_exc(tid, slaveNb, fnNb, data)
                
                # List of words or bytes?
                if isinstance(data, (bytes, bytearray)):
                    if len(data) != 2*nb:
                        raise UserWarning(f'Response data size mismatch. Expected {nb} words ({nb*2} bytes), callback provided {len(data)} bytes')
                        
                    databytes = data
                elif isinstance(data, (list, tuple)):
                    if len(data) != nb:
                        raise UserWarning(f'Response data size mismatch. Expected {nb} words, callback provided {len(data)} words')

                    databytes = bytearray()
                    for w in data:
                        databytes.append(hi(w))
                        databytes.append(lo(w))
                else:
                    raise UserWarning(f'ReadWords should return list, tuple, bytes, bytearray or int. We have {data}')
                    
                
                resp = _mb_create_header_as_bytearray(tid, len(databytes) + 3, slaveNb, fnNb)
                resp.append(len(databytes))
                resp.extend(databytes)
                
                
                return resp
                
            except UserWarning as ex:
                raise UserWarning(f'{FN_NAMES[fnNb]} [slave={slaveNb} addr={addr} nb={nb}]: {ex}')
            
        elif fnNb==5:    # write single bit
            if rtulen!=6:
                raise Exception ("For fn5 rtulen should be 6, not {}".format(rtulen))

            addr = word(rtu[2], rtu[3])
            value = None
            if rtu[4]==0:
                value = 0
            elif rtu[4]==0xFF:
                value = 1
            else:
                raise Exception ("Fn5 requires values to be 0x00/0xFF (not {})".format(rtu[4]))
            
            if rtu[5]!=0:
                raise Exception ("Fn5 rtu[5] should be 0")

            if slaveNb not in MbProtocol.Slaves:
                return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
            slave = MbProtocol.Slaves[slaveNb]
            
            exc = slave.WriteBits(addr, [value])
            if exc!=0:
                return _mb_create_exc(tid, slaveNb, fnNb, exc)
            else:
                msg = _mb_create_header_as_bytearray (tid, 6, slaveNb, fnNb)
                msg.append (rtu[2])
                msg.append (rtu[3])
                msg.append (rtu[4])
                msg.append (rtu[5])
                return msg
                
        elif fnNb==15:    # write bits
            if rtulen<7:
                raise Exception ("Fn15 - invalid rtulen ({})".format(rtulen))

            addr = word(rtu[2], rtu[3])
            nbBits = word(rtu[4], rtu[5])
            nbBytes = word(rtu[6], rtu[7])
            
            if (nbBits % 8) == 0:
                if nbBits != nbBytes*8:
                    raise Exception ("nbBits=={}, nbBytes=={}".format(nbBits, nbBytes))
            else:
                if nbBytes != (1 + int(nbBits/8)):
                    raise Exception ("nbBits=={}, nbBytes=={}".format(nbBits, nbBytes))

            if rtulen!=(8+nbBytes):
                raise Exception ("rtulen({})!=(8+nbBytes({}))".format(rtulen, nbBytes))
                    
            if slaveNb not in MbProtocol.Slaves:
                return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
            slave = MbProtocol.Slaves[slaveNb]
            
            data = []
            
            for iBit in range(nbBits):
                byte = int(iBit / 8)
                bit = iBit % 8
                v = rtu[8 + byte] & (1 << bit)
                data.append ( 1 if v > 0 else 0 )
            
            exc = slave.WriteBits(addr, data)
            if exc!=0:
                return _mb_create_exc(tid, slaveNb, fnNb, exc)
            else:
                msg = _mb_create_header_as_bytearray (tid, 6, slaveNb, fnNb)
                msg.append (rtu[2])
                msg.append (rtu[3])
                msg.append (rtu[4])
                msg.append (rtu[5])
                return msg
                
        elif fnNb==6:    # write single WORD
            if rtulen!=6:
                raise Exception ("Invalid size of request for WRITE WORD: {} instead of 6".format(rtulen))

            addr = word(rtu[2], rtu[3])
            value = word(rtu[4], rtu[5])

            if slaveNb not in MbProtocol.Slaves:
                return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
            slave = MbProtocol.Slaves[slaveNb]
            
            exc = slave.WriteWords(addr, [value])
            if exc:
                return _mb_create_exc(tid, slaveNb, fnNb, exc)
            else:
                msg = _mb_create_header_as_bytearray (tid, 6, slaveNb, fnNb)
                msg.append (rtu[2])
                msg.append (rtu[3])
                msg.append (rtu[4])
                msg.append (rtu[5])
                return msg
                
        elif fnNb==16:    # write multiple WORDs
            if rtulen<9:
                raise Exception ("������� WriteWORDS<F16> ������ ���� �� ����� 9 ���� (� �� {})".format(rtulen))

            addr = word(rtu[2], rtu[3])
            nbWords = word(rtu[4], rtu[5])
            nbBytes = rtu[6]
            
            if (2*nbWords)!=nbBytes:
                raise Exception ("WriteWORDS<F16>: nbWords={}, nbBytes={}".format(nbWords, nbBytes))

            if rtulen!=(7+nbBytes):
                raise Exception ("WriteWORDS<F16>: ����� ����� ������� {}, � ������ ���� {}".format(rtulen,7+nbBytes))
                    
            if slaveNb not in MbProtocol.Slaves:
                return _mb_create_exc(tid, slaveNb, fnNb, EXC_GATEWAY_PROBLEM_1)
            slave = MbProtocol.Slaves[slaveNb]
            
            log.debug(f'{FN_NAMES[fnNb]} [slave={slaveNb} addr={addr} nb={nbWords}]')
            
            as_words = []
            for i in range(nbWords):
                v = word (rtu[7 + i*2], rtu[8 + i*2])
                as_words.append ( v )
            
            try:
                exc = slave.write_words(addr, rtu[7:], as_words)
            except ModbusException as ex:
                log.warning(f'{FN_NAMES[fnNb]} [addr={addr} nb={nbWords}]: {ex}')
                return _mb_create_exc(tid, slaveNb, fnNb, ex.exc_code)
                
            msg = _mb_create_header_as_bytearray (tid, 6, slaveNb, fnNb)
            msg.append(rtu[2])
            msg.append(rtu[3])
            msg.append(rtu[4])
            msg.append(rtu[5])
            return msg
                
        else:
            return _mb_create_exc(tid, slaveNb, fnNb, EXC_ILLEGAL_FN_CODE)

    def CreateReadBitsReply(tid, slaveNb, fnNb, bits):
        nbBits = len(bits)
        nbBytes = int((nbBits/8) if ((nbBits % 8) == 0) else (nbBits/8 + 1))
        
        msg = _mb_create_header_as_bytearray (tid, nbBytes + 3, slaveNb, fnNb)
        msg.append (nbBytes)
        
        globalBitIdx = 0
        for iByte in range(nbBytes):
            byte = 0
            for iBit in range (8):
                if globalBitIdx >= nbBits:
                    break
                if bits[globalBitIdx] != 0:
                    byte |= (1 << iBit)
                globalBitIdx = globalBitIdx + 1
                
            msg.append (byte)
        return msg

    def __str__(self):
        return 'ModbusTCP Server'
        

class MbDevice:
        #returns bits[] or exception nb
    def ReadOutBits(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
        #returns bits[] or exception nb
    def ReadInBits(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
    '''
        ReadOutWords, ReadInWords:
            int                 => EXCEPTION NB
            bytes, bytearray    => raw bytes, передаются как есть
            list, tuple         => массив слов, переводятся в ML-байты
    '''
    def ReadOutWords(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
    def ReadInWords(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
        #returns 0 if success or exception nb
    def WriteBits(self, start, values):
        return EXC_ILLEGAL_FN_CODE

    def write_words(self, addr, data_as_bytes: bytes, data_as_words: tuple) -> None:
        raise Exception()
