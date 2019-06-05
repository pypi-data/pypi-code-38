# -*- coding: utf-8 -*-
# @Time    : 2017/4/27 9:21
# @Author  : Liu Gang
# @Site    : 
# @File    : SignalGenerator.py
# @Software: PyCharm

import visa
import logging.config
from pyvat.vatbase import LOGGER_PATH

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01, 08Jan2019, Liu Gang Add E4438C
V1.00.02, 10Jan2019, Liu Gang Add close_sg
--------------------
"""
SG_DRV_VER = "V1.00.02"
_E4438C = 0
_RS = 1

_INSTR = 'TCPIP0::10.86.20.221::inst0::INSTR'


class SG:
    def __init__(self):
        logging.config.fileConfig(LOGGER_PATH)
        self.logger = logging.getLogger("pysgopr")
        self.inst = None
        self.cableloss = 0
        self.inst_addr = str()
        self.inst_model = _RS
        self.isopen = False

    def open_inst(self, inst_addr=_INSTR):
        if self.isopen is True:
            return
        self.inst_addr = inst_addr
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(self.inst_addr)
        self.isopen = True

    def get_sg_info(self):
        """
        Get inst infomation
        :return:
        """
        return self.inst.query("*IDN?")

    def get_sg_model(self):
        ret_str = self.get_sg_info()
        if ret_str.count("E4438C") != 0:
            self.inst_model = _E4438C
            self.logger.debug("Inst Model:E4438C")
        else:
            self.inst_model = 1
            self.logger.debug("Inst Model:R&S")

    def close_sg(self):
        """
        close inst.
        :return:
        """
        if self.isopen:
            self.isopen = False
            self.inst.close()

        return True

    def reset(self):
        """
        Reset Instr
        :return:
        """
        self.get_sg_model()

        self.inst.write("OUTP:STAT OFF;")
        self.inst.write("*CLS;*WAI;")
        self.inst.write("*RST;*WAI;")

    def set_freq(self, freq):
        """
        Set Frequency   MHz
        :param freq: float
        :return:
        """
        if self.inst_model == _E4438C:
            self.inst.write(":SOUR:FREQ:CW %fMHZ;" % freq)
        else:
            self.inst.write(":SOUR:FREQ %fMHZ;" % freq)

    def set_power(self, power):
        """
        Set Power
        :param power: float
        :return:
        """
        power += self.cableloss
        self.inst.write(":SOUR:POW %fdbm;" % power)

    def set_rfen(self, onoff=1):
        """
        Set RF Switch ON OFF
        :param onoff: 1 on, 0 off
        :return:
        """
        if self.inst_model == _E4438C:
            if onoff == 1:
                self.inst.write(":OUTP:STAT ON")
            else:
                self.inst.write(":OUTP:STAT OFF")
        else:
            if onoff == 1:
                self.inst.write(":OUTP:ALL:STAT ON")
            else:
                self.inst.write(":OUTP:ALL:STAT OFF")

    def set_data(self, sel=1):
        """
        Set waveform files.
        :param sel:1.20070409miller2 6700 backward calibration
                    2.081220etc, 9800 Rssi Test
        :return:
        """
        if self.inst_model == _E4438C:
            return

        if sel == 1:
            self.inst.write("SOUR:BB:ARB:WAV:SEL '/var/user/share/20070409miller2.wv'")
        elif sel == 2:
            self.inst.write("SOUR:BB:ARB:WAV:SEL '/var/user/share/081220etc.wv'")
        else:
            print("No such waveform option now.")

    def set_trigger(self, sel=1):
        """
        set trigger
        :param sel:1, on ,,else off.
        :return:
        """
        self.inst.write(":SOUR:BB:ARB:SEQ SING")
        # self.inst.write(":SOUR:BB:ARB:TRIG:SLUN SEQ")
        # self.inst.write(":SOUR:BB:ARB:TRIG:SLEN 1")
        if sel == 1:
            self.inst.write(":SOUR:BB:ARB:TRIG:SOUR INT")
        else:
            self.inst.write(":SOUR:BB:ARB:TRIG:SOUR EXT")

    def set_mod(self, sel=1):
        """
        Set moduate state
        :param sel: 1, on. else off.
        :return:
        """
        if sel == 1:
            self.inst.write(":SOUR:BB:ARB:STAT ON;")
        else:
            self.inst.write(":SOUR:BB:ARB:STAT OFF;")

    def set_iq(self, sel=1):
        """
        Set source IQ on off
        :param sel: 1, for ON, else for OFF
        :return:
        """
        if sel == 1:
            self.inst.write(":SOUR:IQ:STAT ON")
        else:
            self.inst.write(":SOUR:IQ:STAT OFF")

    def set_trig_exec(self, sel=1):
        """
        Set trig on off
        :param sel: 1 for on, else for off.
        :return:
        """
        if sel == 1:
            self.inst.write(":SOUR:BB:ARB:TRIG:EXEC")


def test():
    sg = SG()
    sg.open_inst()
    sg.reset()
    sg.set_data(2)
    sg.set_trigger(1)
    sg.set_iq(1)
    sg.set_freq(5783)
    sg.set_power(-65)
    sg.set_rfen(0)
    sg.set_iq(2)
    sg.set_trig_exec(1)


if __name__ == "__main__":
    test()
