'''
    Имитирует Сепам с осциллограммами
'''
import datetime
import enum

from .modbus import *
from ..tools import *
from ..vector import Vector
from .opg import OpgDat, OpgCfg


class SepamType(enum.Enum):
    S20 = 'S20'
    S40 = 'S40'
    S80 = 'S80'
    S2K = 'S2K'


class OpgRecord:
    def __init__(self, nb):
        self.Nb = nb
        self.Exists = False
        self.Dtm = None

    def generate(self):
        self.Exists = True
        self.Dtm = datetime.datetime.now()
        
    def get_dtm(self) -> (bytes, bytearray):
        if not self.Exists:
            return b'\0' * 8

        d = self.Dtm
        y = d.year - 2000
        ss = d.second * 1000 + d.microsecond // 1000
        return bytes([hi(y), lo(y), d.month, d.day, d.hour, d.minute, hi(ss), lo(ss)])

g_OpgDat = OpgDat
g_OpgCfg = OpgCfg
g_Opg = g_OpgCfg + g_OpgDat

class Sepam:
    def __init__(self, sepam_type, log):
        assert isinstance(sepam_type, SepamType), sepam_type
        
        self.log = log
        self.SepamType = sepam_type
        self.Records = []
        self.SelectedOpg = None
        self.AcknowledgedPortionsNb: int = None

        maxOpg = None
        if sepam_type == SepamType.S20:
            self.StatusVector = Vector(0x2204, size=37)
            self.SelectVector = Vector(0x2200, size=4)
            self.RdBlockVector = Vector(0x2300, size=125)
            self.AckBlockVector = Vector(self.RdBlockVector.s, size=1)
            maxOpg = 2
            
        elif sepam_type == SepamType.S40:
            self.StatusVector = Vector (0x2204, size=82)
            self.SelectVector = Vector (0x2200, size=4)
            self.RdBlockVector = Vector (0x2300, size=125)
            self.AckBlockVector = Vector (self.RdBlockVector.s, size=1)
            maxOpg = 19
            
        elif sepam_type == SepamType.S80:
            self.StatusVector = Vector (0x400, size=80) # в некоторых местах 80, в других 82
            self.SelectVector = Vector (0x2200, size=4)
            self.RdBlockVector = Vector (0x2300, size=125)
            self.AckBlockVector = Vector (self.RdBlockVector.s, size=1)
            maxOpg = 19
            
        elif sepam_type == SepamType.S2K:
            self.StatusVector = Vector(0xD204, size=13)
            self.SelectVector = Vector(0xD200, size=4)
            self.RdBlockVector = Vector(0xD300, size=125)
            self.AckBlockVector = Vector(self.RdBlockVector.s, size=1)
            maxOpg = 2
            
        else:
            raise Exception()
        
        for i in range(maxOpg):
            self.Records.append (OpgRecord(i+1))
            
        self.record_new()
        
    def record_new(self):
        for rec in self.Records:
            if not rec.Exists:
                rec.generate()
                self.log.info(f'Recorded new OPG #{rec.Nb} on {rec.Dtm}')
                return
        rec = self.Records[0]
        self.log.info(f'Recorded new OPG #{rec.Nb} on {rec.Dtm}')
        rec.generate()
    
        
        #returns bits[] or exception nb
    def ReadOutBits(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
        #returns bits[] or exception nb
    def ReadInBits(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
        #returns words[] or exception nb
    def ReadOutWords(self, start, nb):
        
        log = self.log
        req_vec = Vector(start, size=nb)
        
        # Read STATUS
        if req_vec.Intersects(self.StatusVector):
            if not req_vec.IsEqual(self.StatusVector):
                raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, f'Partial overlap: req={req_vec}; STATUS={self.StatusVector}')
            
            data = bytearray()
            
            nb_existing = len([filter(lambda x: x.Exists, self.Records)])
            
            if self.SepamType == SepamType.S20:
                add_word(data, 0)
                add_word(data, 0)
                add_word(data, len(g_OpgCfg))
                add_word(data, len(g_OpgDat))
                add_word(data, nb_existing)
            
            elif self.SepamType == SepamType.S40:
                add_word(data, 0)
                add_word(data, 0)
                add_word(data, len(g_OpgCfg))
                add_word(data, len(g_OpgDat) >> 16)
                add_word(data, len(g_OpgDat) & 0xffff)
                add_word(data, nb_existing)

            elif self.SepamType == SepamType.S80:
                add_word(data, len(g_OpgCfg))
                add_word(data, len(g_OpgDat) >> 16)
                add_word(data, len(g_OpgDat) & 0xffff)
                add_word(data, nb_existing)

            else:
                add_word(data, 0)
                add_word(data, 0)
                add_word(data, len(g_OpgCfg))
                add_word(data, len(g_OpgDat))
                add_word(data, nb_existing)

            for rec in self.Records:
                data.extend(rec.get_dtm())

            return data
        
        # Read block
        elif req_vec.Intersects(self.RdBlockVector):
            if not req_vec.IsEqual(self.RdBlockVector):
                raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, f'Partial overlap: req={req_vec}; RD_BLOCK={self.RdBlockVector}')
                
            if self.SelectedOpg is None:
                raise ModbusException(EXC_CANT_PROCESS_FN, 'Opg is not selected, cant read block')

            portion = min((self.bytesRemain(), 248))
            data = bytearray()
            data.append(self.xNb())
            data.append(portion)
            
            sent = self.AcknowledgedPortionsNb * 248
            
            data.extend(g_Opg[sent:sent+portion])
            if portion < 248:   # добить нулями
                data.extend(b'\0' * (248-portion))
            
            return data
        else:
            raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, 'No overlaps')
        
        #returns words[] or exception nb
    def ReadInWords(self, start, nb):
        return EXC_ILLEGAL_FN_CODE
        
        #returns 0 if success or exception nb
    def WriteBits(self, start, values):
        return EXC_ILLEGAL_FN_CODE

    def write_words(self, addr, data_as_bytes: bytes, data_as_words: tuple) -> None:
        log = self.log
        req_vec = Vector(addr, size=len(data_as_words))
    
        # Select opg
        if req_vec.Intersects(self.SelectVector):
            if not req_vec.IsEqual(self.SelectVector):
                raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, f'Partial overlap: req={req_vec}; SELECT={self.SelectVector}')
                
            self.SelectedOpg = None
            for rec in self.Records:
                if rec.Exists:
                    dtm = rec.get_dtm();
                    if dtm == data_as_bytes:
                        self.SelectedOpg = rec
                        break

            if self.SelectedOpg is None:
                raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, f'Cant select opg: no datetime match')
            self.AcknowledgedPortionsNb = 0
            return 0
        
        # Ack block
        elif req_vec.Intersects(self.AckBlockVector):
            if not req_vec.IsEqual(self.AckBlockVector):
                raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, f'Partial overlap: req={req_vec}; ACK_BLOCK={self.AckBlockVector}')

            if self.SelectedOpg is None:
                raise ModbusException(EXC_CANT_PROCESS_FN, 'No opg selected, cant ack block')
            
            xnb = self.AcknowledgedPortionsNb & 0xff

            if data_as_words[0] != (xnb << 8):
                raise ModbusException(EXC_CANT_PROCESS_FN, f'Ack mismatches exchange number. Ack={data_as_words[0]}, xnb={xnb << 8}')

            self.AcknowledgedPortionsNb += 1

            if self.bytesRemain() == 0:
                self.SelectedOpg = None

            return 0
        
        else:
            raise ModbusException(EXC_ILLEGAL_DATA_ADDRESS, 'No overlaps')

    def xNb(self) -> int:
        return self.AcknowledgedPortionsNb & 0xFF

    def bytesRemain(self) -> int:
        sent = self.AcknowledgedPortionsNb * 248
        return len(g_Opg) - sent

