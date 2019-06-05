#coding:utf-8
from __future__ import (print_function, unicode_literals)
"""
2字节的CRC-ITU 比特位对应校验的数据的比特位之间的关系
CRC15   =>              3,7
CR14    =>              2,6
CR13    =>              1,5
CR12    =>              0,4
C411    =>              3
CR10    =>2, CR15   =>  2, 3,7
CR9     =>1, CR14   =>  1, 2,6
CR8     =>0, CR13   =>  0, 1,5

CR7     =>   CR12   =>  0,4
CR6                 =>  3
CR5                 =>  2
CR4                 =>  1
CR3     => 0, CR15  =>  0,3,7
CR2     =>    CR14  =>   2,6
CR1     =>    CR13  =>   1,5
CR0     =>    CR12  =>   0,4
"""

def get_bytecrc_itu(ucChar, uslpwCrc):
    tmpChar = ucChar ^ (uslpwCrc & 0x00FF)
    tmpChar = (tmpChar ^ (tmpChar << 4))

    tmp = tmpChar & 0x00FF

    usNewlpwCrc = (uslpwCrc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)

    return usNewlpwCrc


def get_bytecrc_itu2(ucChar, uslpwCrc):
    databit7 = (ucChar >> 7) & 0x0001
    databit6 = (ucChar >> 6) & 0x0001
    databit5 = (ucChar >> 5) & 0x0001
    databit4 = (ucChar >> 4) & 0x0001
    databit3 = (ucChar >> 3) & 0x0001
    databit2 = (ucChar >> 2) & 0x0001
    databit1 = (ucChar >> 1) & 0x0001
    databit0 = (ucChar >> 0) & 0x0001

    crc15 =  (uslpwCrc >> 15) & 0x0001
    crc14 =  (uslpwCrc >> 14) & 0x0001
    crc13 =  (uslpwCrc >> 13) & 0x0001
    crc12 =  (uslpwCrc >> 12) & 0x0001
    crc11 =  (uslpwCrc >> 11) & 0x0001
    crc10 =  (uslpwCrc >> 10) & 0x0001
    crc9 =  (uslpwCrc >> 9) & 0x0001
    crc8 =  (uslpwCrc >> 8) & 0x0001
    crc7 =  (uslpwCrc >> 7) & 0x0001
    crc6 =  (uslpwCrc >> 6) & 0x0001
    crc5 =  (uslpwCrc >> 5) & 0x0001
    crc4 =  (uslpwCrc >> 4) & 0x0001
    crc3 =  (uslpwCrc >> 3) & 0x0001
    crc2 =  (uslpwCrc >> 2) & 0x0001
    crc1 =  (uslpwCrc >> 1) & 0x0001
    crc0 =  (uslpwCrc >> 0) & 0x0001

    # CRC Byte2
    newcrcbit15 = databit7 ^ crc7 ^ databit3 ^ crc3
    newcrcbit14 = databit6 ^ crc6 ^ databit2 ^ crc2
    newcrcbit13 = databit5 ^ crc5 ^ databit1 ^ crc1
    newcrcbit12 = databit4 ^ crc4 ^ databit0 ^ crc0

    newcrcbit11 =           databit3 ^ crc3
    newcrcbit10 = newcrcbit15 ^ databit2 ^ crc2
    newcrcbit9  = newcrcbit14 ^ databit1 ^ crc1
    newcrcbit8  = newcrcbit13 ^ databit0 ^ crc0

    # CRC Byte1
    newcrcbit7 = newcrcbit12 ^ crc15
    newcrcbit6 = databit3 ^ crc3 ^ crc14
    newcrcbit5 = databit2 ^ crc2 ^ crc13
    newcrcbit4 = databit1 ^ crc1 ^ crc12

    newcrcbit3 = newcrcbit15 ^ databit0 ^ crc0 ^ crc11
    newcrcbit2 = newcrcbit14 ^ crc10
    newcrcbit1 = newcrcbit13 ^ crc9
    newcrcbit0 = newcrcbit12 ^ crc8

    newcrc = (newcrcbit15 << 15) | (newcrcbit14 << 14) | (newcrcbit13 << 13) | (newcrcbit12 << 12) |\
            (newcrcbit11 << 11) | (newcrcbit10 << 10) | (newcrcbit9 << 9) | (newcrcbit8 << 8) |\
            (newcrcbit7 << 7) | (newcrcbit6 << 6) | (newcrcbit5 << 5) | (newcrcbit4 << 4) |\
            (newcrcbit3 << 3) | (newcrcbit2 << 2) | (newcrcbit1 << 1) | (newcrcbit0 << 0)

    return newcrc

def get_crc_itu(data):
    initCrc = 0x6363
    lpwCrc = initCrc
    if isinstance(data, (list, str)):
        for ch in data:
            if isinstance(ch, int):
                tmpdata = ch
            elif isinstance(ch, str):
                tmpdata = ord(ch)
            lpwCrc = get_bytecrc_itu2(tmpdata, lpwCrc)
    elif isinstance(data, int):
            lpwCrc = get_bytecrc_itu2(data, lpwCrc)

    return lpwCrc

if __name__ == "__main__":
    data = [0x00, '\x00']
    data = "\x12\x34"
    crc = get_crc_itu(data)
    print(hex(crc), bytearray(crc))

