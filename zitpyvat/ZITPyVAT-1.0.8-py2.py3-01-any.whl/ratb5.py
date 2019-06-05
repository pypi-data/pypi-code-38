# -*- coding: utf-8 -*-
# @Time    : 2017/3/11 15:44
# @Author  : Liu Gang
# @Site    : 
# @File    : ratb5.py
# @Software: PyCharm Community Edition
import socket
import struct
import sys
from time import sleep

__all__ = ["RATB5", "RATB5_VER"]

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01
--------------------
"""
RATB5_VER = "V1.00.01"

_ADDR = ("10.86.20.223", 8001)

RATB_GPIO_VALUE = 0x09
RATB_GPIO_DIR = 0x10
RATB_ANT_SEL = 0x1A
RATB_INS_SEL = 0x1B
RATB_CODE_SEL = 0x1D
RATB_RATE_SEL = 0x1E
RATB_DATT_CFG = 0x1F
RATB_SEND_EN = 0x1C
RATB_FRAME_CNT = 0x20
RATB_FRAME_GAP = 0x21
RATB_RELAY_STAT = 0x22
RATB_PROTOCOL_SEL = 0x23
RATB_RS485_SEL = 0x25  # 0 for 6700, 1 for 6710. default 0
RATB_DATT1_T900 = 0x02
RATB_DATT2_T900 = 0x03
RATB_MOD1_EN = 0x28
RATB_MOD2_EN = 0x29

ANT_INS_SA = 1
ANT_INS_SG = 2

T800 = 0
T900 = 1


class TagRatbMsg:
    def __init__(self):
        self.ucRW = 0x00
        self.ucAddr = 0x00
        self.ucHData = 0x00
        self.ucLData = 0x00


class RATB5:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.req = TagRatbMsg()
        self.rev = TagRatbMsg()
        self.datt1 = 13.0
        self.ratb_ver = T800  # T800 0, T900 1
        if sys.version > '3':
            self.py_ver = 3
        else:
            self.py_ver = 2

    def __del__(self):
        self.s.close()

    def set_ratb_ver(self, ver):
        """
        Set Version
        :param ver: 0, T800; 1, T900
        :return:None
        """
        self.ratb_ver = ver

    # @staticmethod
    def chrtobyte(self, in_list):
        """
        in_list(char) -> out_str(string)
        :param in_list:
        :return:out_list (string)
        """
        # print(in_list)
        if self.py_ver == 3:
            out_str = bytes(in_list)
        else:
            out_str = str()
            for c in in_list:
                out_str += struct.pack('B', c)

        print(out_str)
        return out_str

    def msg_gen(self, addr, data=0x00, mod=1):
        if mod == 1:
            self.req.ucRW = 0xC0
            self.req.ucAddr = addr
            self.req.ucHData = (data >> 8) & 0xFF
            self.req.ucLData = data & 0xFF
        if mod == 0:
            self.req.ucRW = 0xA0
            self.req.ucAddr = addr
            self.req.ucHData = 0x00
            self.req.ucLData = 0x00

        req_list = list()
        req_list.append(self.req.ucRW)
        req_list.append(self.req.ucAddr)
        req_list.append(self.req.ucHData)
        req_list.append(self.req.ucLData)
        for x in range(28):
            req_list.append(0x00)

        return self.chrtobyte(req_list)

    def rev_gen(self, data_list):
        self.rev.ucRW = data_list[0]
        self.rev.ucAddr = data_list[1]
        self.rev.ucHData = data_list[2]
        self.rev.ucLData = data_list[3]

    def data_read(self, tsec):
        self.s.settimeout(tsec)
        try:
            data, addr = self.s.recvfrom(1024)
            ret_list = []
            if self.py_ver == 3:
                for s in data:
                    ret_list.append(s)
            else:
                for s in data:
                    ret_list.append(struct.unpack('B', s)[0])
            print(ret_list)
            return ret_list
        except Exception as e:
            print(e.args[0])
            return None

    def send_msg(self, addr, data):
        global _ADDR
        c = self.s.sendto(self.msg_gen(addr, data), _ADDR)
        if c <= 0:
            print("Fail")
            return False

    def query_msg(self, addr, timeout):
        global _ADDR
        c = self.s.sendto(self.msg_gen(addr, mod=0), _ADDR)
        if c <= 0:
            print("Send Fail")
            return None

        revlist = self.data_read(timeout)
        if revlist is None:
            return None
        else:
            self.rev_gen(revlist)

        return (self.rev.ucHData << 8) | self.rev.ucLData

    def sw_ant(self, ant, ins):
        """
        181218 Liugang Add T900
        :param ant: Ant Number
        :param ins: Instrument Code
        :return:
        """
        if self.ratb_ver == T800:
            self.send_msg(RATB_ANT_SEL, 0x01 << (ant - 1))
        elif self.ratb_ver == T900:
            self.send_msg(RATB_ANT_SEL, ant - 1)

        sleep(0.02)
        self.send_msg(RATB_INS_SEL, ins)
        sleep(0.02)

    def set_gpio(self, value):
        self.send_msg(RATB_GPIO_DIR, 0x01)  # set GPIO output dir
        sleep(0.02)
        self.send_msg(RATB_GPIO_VALUE, value)
        sleep(0.02)

    def read_gpio(self):
        self.send_msg(RATB_GPIO_DIR, 0x00)  # set GPIO input dir
        sleep(0.02)
        return self.query_msg(RATB_GPIO_VALUE, 5)  # read GPIO value ,5s timeout

    def set_rssi_rate(self, rate):
        # req = 0x00
        if rate == 64:
            req = 0x01
        elif rate == 174:
            req = 0x02
        elif rate == 320:
            req = 0x04
        elif rate == 640:
            req = 0x08
        elif rate == 160:
            req = 0x09
        elif rate == 274:
            req = 0x0B
        elif rate == 80:
            req = 0x0A
        else:
            return False

        self.send_msg(RATB_RATE_SEL, req)
        return True

    def set_frame_gap(self, gap):
        self.send_msg(RATB_FRAME_GAP, gap)
        return True

    def set_protocol(self, pro):
        """

        :param pro:1 , 6C   .2, HangBiao
        :return:
        """
        self.send_msg(RATB_PROTOCOL_SEL, pro)
        return True

    def set_rssi_code(self, code):
        """

        :param code: 1,FM0 2,Miller2
        :return:
        """
        self.send_msg(RATB_CODE_SEL, code)
        return True

    def set_rssi_datt(self, datt):
        self.send_msg(RATB_DATT_CFG, datt)
        return True

    def set_frame_cnt(self, cnt):
        self.send_msg(RATB_FRAME_CNT, cnt)
        return True

    def rssi_send_en(self):
        self.send_msg(RATB_SEND_EN, 0x01)
        return True

    def datt_cal(self, datt=float()):
        """

        :param datt: dbm to  attenuate
        :return:datt config for RATB5
        """
        f_datt = self.datt1
        i_target0 = int(f_datt)
        hdatt = i_target0 << 1
        f_gap0 = f_datt - i_target0
        if f_gap0 >= 0.75:
            hdatt += 2
        elif 0.75 > f_gap0 >= 0.25:
            hdatt += 1
        hdatt = ~hdatt & 0xff
        hdatt &= 0x3f

        datt -= f_datt

        i_target = int(datt)
        ldatt = i_target << 1
        f_gap = datt - i_target
        if f_gap >= 0.75:
            ldatt += 2
        elif 0.75 > f_gap >= 0.25:
            ldatt += 1
        ldatt = ~ldatt & 0xff
        ldatt &= 0x3f

        return ((hdatt << 6) | ldatt) & 0xfff

    def rs485_sel(self, sel):
        """
        Sel Rs485 test mode
        :param sel:1 for 6710, 0 is default,for 6700
        :return:
        """
        self.send_msg(RATB_RS485_SEL, sel)
        return True


def test():
    ue = RATB5()
    # ue.datt_cal(18)
    ue.set_rssi_datt(0xfff)
    ue.read_gpio()
    # while True:
    #     print("1. 6C\n2. Hangbiao\n0. Exit")
    #     sel = eval(input("Your selection:"))
    #     if sel == 1 or sel == 2:
    #         ue.send_msg(0x23, 0x01 << (sel - 1))
    #     else:
    #         break
    #
    #     print("1. FM0\n 2. Miller2\n0. Exit")
    #     sel = eval(input("Your selection:"))
    #     if sel == 1:
    #         ue.send_msg(RATB_CODE_SEL, 0x01)
    #     elif sel == 2:
    #         ue.send_msg(RATB_CODE_SEL, 0x02)
    #     else:
    #         break
    #
    #     print("1. 160\n2. 174\n3. 274\n4. 64\n0. Exit")
    #     sel = eval(input("Your selection:"))
    #     if sel == 1:
    #         ue.send_msg(RATB_RATE_SEL, 0x09)
    #     elif sel == 2:
    #         ue.send_msg(RATB_RATE_SEL, 0x02)
    #     elif sel == 3:
    #         ue.send_msg(RATB_RATE_SEL, 0x0B)
    #     elif sel == 4:
    #         ue.send_msg(RATB_RATE_SEL, 0x01)
    #     else:
    #         break
    #
    #     sel = eval(input("Frame Gap:"))
    #     ue.send_msg(RATB_FRAME_GAP, int(sel))
    #     sel = eval(input("Frame Count:"))
    #     ue.send_msg(RATB_FRAME_CNT, int(sel))
    #     input("AnyKey to Start:")
    #     ue.send_msg(RATB_SEND_EN, 0x01)
    #     input("Done")
    #
    # print("Exit")


if __name__ == "__main__":
    test()
