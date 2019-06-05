# -*- coding: utf-8 -*-
# @Time    : 2018/1/18 15:46
# @Author  : Liu Gang
# @Site    : 
# @File    : py_sa_opr.py
# @Software: PyCharm Community Edition
import visa
from pyvisa.errors import VisaIOError
from time import sleep
from math import fabs
import logging.config
from pyvat.vatbase import LOGGER_PATH

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01, 28May2018, Liu Gang,,Add ACPR,OBW E4445 Commands
--------------------
"""
SA_DRV_VER = "V1.00.01"

_E4445A = 0
_N9010 = 1


class SA:
    def __init__(self):
        self.isopen = False
        logging.config.fileConfig(LOGGER_PATH)
        self.logger = logging.getLogger("pysaopr")
        self.inst = None
        self.inst_model = int()
        # print "Start Open", time()
        # try:
        #     self.inst = self.rm.open_resource(str_addr)
        # except VisaIOError:
        #     self.isopen = False
        #     self.logger.error("SA Open Error")
        # else:
        #     self.isopen = True
        #     self.logger.debug("SA Open Success")
        #     self.inst.write(":CAL:AUTO OFF")
        # print "Open Finish", time()

    def __del__(self):
        if self.isopen:
            self.close_sa()

    def write(self, str_cmd):
        if self.isopen is False:
            return 0
        else:
            return self.inst.write(str_cmd)

    def open_sa(self, str_addr="TCPIP0::10.86.20.222::inst0::INSTR"):
        """
        Open SA.
        if is Open ,set auto cal off.
        :param str_addr: inst IP addr
        :return:BOOL
        """
        if self.isopen:
            pass
        else:
            try:
                rm = visa.ResourceManager()
                self.inst = rm.open_resource(str_addr)
            except VisaIOError:
                self.isopen = False
                self.logger.error("SA Open Error")
                return False
            else:
                self.isopen = True
                self.logger.debug("SA Open Success")

        if self.get_sa_model() == -1:
            return False

        self.set_timeout(10000)

        if self.isopen:
            self.write(":CAL:AUTO OFF")

        return self.isopen

    def get_sa_info(self):
        """
        Get inst infomation
        :return:
        """
        return self.inst.query("*IDN?")

    def get_error_info(self):
        pass

    def get_sa_model(self):
        ret_str = self.get_sa_info()
        if ret_str.count("E4445A") != 0:
            self.inst_model = _E4445A
            self.logger.debug("Inst Model:E4445A")
        elif ret_str.count("N9010") != 0 or ret_str.count("N9020") != 0:
            self.inst_model = _N9010
            self.logger.debug("Inst Model:N9020")
        else:
            self.inst_model = -1
            self.logger.debug("Inst Model:Not Support")

    def close_sa(self):
        """
        close inst.
        if is Open ,set auto cal back on .
        :return:
        """
        if self.isopen:
            if self.inst_model == _E4445A:
                self.write(":CAL:AUTO ALER")
            else:
                self.write(":CAL:AUTO ON")
            self.isopen = False
            self.inst.close()
            self.logger.debug("Set Auto Cal On,Close SA")
        return True

    def set_cent_freq(self, f_freq):
        """
        Set center Freq
        :param f_freq:KHz
        :return:
        """
        self.write(":SENS:FREQ:CENT {0}KHz".format(f_freq))
        ret_freq = float(self.inst.query(":SENS:FREQ:CENT?")) / 1000
        if ret_freq == f_freq:
            self.logger.debug("Set Cent Freq {0}KHz Success".format(f_freq))
            return True
        else:
            self.logger.error("Set Cent Freq {0}KHz Fail".format(f_freq))
            return False

    def set_timeout(self, f_timeout):
        """
        config time out
        :param f_timeout:ms
        :return:
        """
        self.inst.timeout = f_timeout
        return True

    def sel_meas_mode(self):
        pass

    def conf_meas_mode(self, i_mode=0):
        """
        config measuer mode
        :param i_mode:0,SAN 1, ACPR; 2 OBW;
        :return:
        """
        if i_mode == 0:
            str_cmd = "SAN"
        elif i_mode == 1:
            str_cmd = "ACP"
        elif i_mode == 2:
            str_cmd = "OBW"
        else:
            self.logger.error("No Such Option:{0}".format(i_mode))
            return False

        self.write("CONF:{0}".format(str_cmd))
        ret_mode = str(self.inst.query("CONF?"))
        if ret_mode.count(str_cmd) != 0:
            self.logger.debug("Config to {0} Mode Success".format(str_cmd))
            return True
        else:
            self.logger.error("Config to {0} Mode Fail".format(str_cmd))
            return False

    def set_cont_mode(self, i_mode=1):
        """
        Set Continue or Single mode
        :param i_mode: 0,Single, 1, Con
        :return:
        """
        str_cmd = ":INIT:CONT"
        if i_mode == 0:
            str_type = "OFF"
        elif i_mode == 1:
            str_type = "ON"
        else:
            self.logger.warning("no such mode")
            return False
        self.write(str_cmd + " {0}".format(str_type))
        ret = self.inst.query(str_cmd + "?")
        if int(ret) != i_mode:
            self.logger.error("Set Cont Mode {0} Fail".format(str_type))
            return False
        else:
            self.logger.debug("Set Cont Mode {0} Success".format(str_type))
            return True

    def set_avg_count(self, i_count):
        """
        Set average Count
        :param i_count: times
        :return:
        """
        self.write(":SENS:AVER:COUN {0}".format(i_count))
        ret_count = float(self.inst.query(":SENS:AVER:COUN?"))
        if ret_count == i_count:
            self.logger.debug("Set Average Count {0} Success".format(i_count))
            return True
        else:
            self.logger.error("Set Average Count {0} Fail".format(i_count))
            return False

    def sel_avg_mode(self):
        pass

    def set_ref_level(self, i_level):
        """
        Set Ref Level
        :param i_level: Y Level  ,dBm
        :return:
        """
        if i_level > 20:
            i_level = 20
        self.write(":DISP:WIND:TRAC:Y:RLEV {0}dBm".format(i_level))
        ret_lvl = self.get_ref_level()
        if fabs(ret_lvl - i_level) < 1:
            self.logger.debug("Set Ref Level {0} Success".format(i_level))
            return True
        else:
            self.logger.error("Set Ref Level {0} Fail".format(i_level))
            return False

    def get_ref_level(self):
        ret_lvl = float(self.inst.query(":DISP:WIND:TRAC:Y:RLEV?"))
        self.logger.debug("Get Ref Level {0}dBm".format(ret_lvl))
        return ret_lvl

    def set_input_atten(self, i_atten):
        """

        :param i_atten: input attenuation value
        :return:
        """
        str_cmd = ":SENS:POW:RF:ATT"
        self.write(str_cmd + " {0}".format(i_atten))
        ret_att = self.get_input_atten()
        if ret_att == i_atten:
            self.logger.debug("Set Input Atten {0} Success".format(i_atten))
            return True
        else:
            self.logger.error("Set Input Atten {0} Fail".format(i_atten))
            return False

    def get_input_atten(self):
        """
        Get input attenuation.
        :return:dB
        """
        str_cmd = ":SENS:POW:RF:ATT"
        ret_att = float(self.inst.query(str_cmd + "?"))
        self.logger.debug("Get Atten {0}dB".format(ret_att))
        return ret_att

    def set_sweep_time(self, f_time):
        """
        :param f_time: ms
        :return:
        """
        str_cmd = ":SENS:SWE:TIME"
        self.write(str_cmd + " {0}ms".format(f_time))
        if float(self.inst.query(str_cmd + "?")) * 1000 == f_time:
            self.logger.debug("Set Sweep Time:{0}ms Success".format(f_time))
            return True
        else:
            self.logger.error("Set Sweep Time:{0}ms Fail".format(f_time))
            return False

    def set_span(self, f_span):
        """
        Set Span
        :param f_span: KHz
        :return:
        """
        str_cmd = ":SENS:FREQ:SPAN"
        if f_span > 1000:
            f_span = float(f_span) / 1000
            self.write(str_cmd + " {0}MHz".format(f_span))
            f_span *= 1000
        else:
            self.write(str_cmd + " {0}KHz".format(f_span))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_span:
            self.logger.debug("Set Span:{0}KHz Success".format(f_span))
            return True
        else:
            self.logger.error("Set Span:{0}KHz Fail".format(f_span))
            return False

    def set_rbw(self, f_rbw):
        """
        Set Rfw
        :param f_rbw:KHz
        :return:
        """
        str_cmd = ":SENS:BAND:RES"
        self.write(str_cmd + " {0}KHz".format(f_rbw))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_rbw:
            self.logger.debug("Set RBW:{0}KHz Success".format(f_rbw))
            return True
        else:
            self.logger.error("Set RBW:{0}KHz Fail".format(f_rbw))
            return False

    def set_vbw(self, f_vbw):
        pass

    def set_acpr_offset_freq(self, list_freq):
        """
        Set acpr meas offset frequence
        :param list_freq:KHz
        :return:
        """
        str_cmd = ":ACP:OFFS1:LIST:STAT 1"
        i_cnt = len(list_freq)
        for x in xrange(i_cnt - 1):
            str_cmd += ",1"
        self.write(str_cmd)

        str_cmd = ":ACP:OFFS1:LIST {0}KHz".format(list_freq[0])
        for x in range(1, i_cnt):
            str_cmd += ",{0}KHz".format(list_freq[x])
        self.write(str_cmd)
        self.logger.debug("Config ACPR OFFSET Finish")
        return True

    def set_acpr_ch_bw(self, list_bw):
        """
        config band width
        :param list_bw:each offsetband width
        :return:
        """
        i_cnt = len(list_bw)
        str_cmd = ":ACP:OFFS1:LIST:BAND {0}KHz".format(list_bw[0])
        for x in range(1, i_cnt):
            str_cmd += ",{0}KHz".format(list_bw[x])
        self.write(str_cmd)
        self.logger.debug("Config ACPR OFFSET BANDWIDTH Finish")
        return True

    def set_acpr_span(self, f_span):
        """
        Set ACPR meas Span,,,It need to be config at last
        :param f_span:KHz
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_span(f_span)

        str_cmd = ":ACP:FREQ:SPAN"
        self.write(str_cmd + " {0}KHz".format(f_span))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_span:
            self.logger.debug("Set ACPR Span:{0}KHz Success".format(f_span))
            return True
        else:
            self.logger.error("Set ACPR Span:{0}KHz Fail".format(f_span))
            return False

    def set_acpr_carr_cnt(self, i_cnt=1):
        """
        Set ACPR Meas Carrier count.
        normal is 1.
        :param i_cnt:
        :return:
        """
        str_cmd = ":ACP:CARR:COUN {0}".format(i_cnt)
        self.write(str_cmd)
        return True

    def set_acpr_rbw(self, f_rbw):
        """
        Set ACPR rbw
        :param f_rbw:KHz
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_rbw(f_rbw)

        str_cmd = ":ACP:BAND"
        self.write(str_cmd + " {0}KHz".format(f_rbw))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_rbw:
            self.logger.debug("Set ACPR RBW:{0}KHz Success".format(f_rbw))
            return True
        else:
            self.logger.error("Set ACPR RBW:{0}KHz Fail".format(f_rbw))
            return False

    def set_acpr_space(self, f_space):
        """
        Config Carrier Space
        :param f_space: KHz
        :return:
        """
        if self.inst_model == _E4445A:
            return True

        str_cmd = ":ACP:CARR:LIST:WIDT"
        self.write(str_cmd + " {0}KHz".format(f_space))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_space:
            self.logger.debug("Set Carrier Space:{0}KHz Success".format(f_space))
            return True
        else:
            self.logger.error("Set Carrier Space:{0}KHz Fail".format(f_space))
            return False

    def set_acpr_carr_band(self, f_band):
        """
        Config Carrier Bandwidth
        :param f_band:KHz
        :return:
        """
        if self.inst_model == _E4445A:
            str_cmd = ":ACP:BAND:INT"
        else:
            str_cmd = ":ACP:CARR:LIST:BAND"
        self.write(str_cmd + " {0}KHz".format(f_band))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_band:
            self.logger.debug("Set Carrier bandwidth:{0}KHz Success".format(f_band))
            return True
        else:
            self.logger.error("Set Carrier bandwidth:{0}KHz Fail".format(f_band))
            return False

    def set_acpr_sweep(self, f_time):
        """
        Set ACPR Sweep Time
        :param f_time: ms
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_sweep_time(f_time)
        str_cmd = ":ACP:SWE:TIME"
        self.write(str_cmd + " {0}ms".format(f_time))
        if float(self.inst.query(str_cmd + "?")) * 1000 == f_time:
            self.logger.debug("Set ACPR Sweep Time:{0}ms Success".format(f_time))
            return True
        else:
            self.logger.error("Set ACPR Sweep Time:{0}ms Fail".format(f_time))
            return False

    def set_acpr_avg_cnt(self, i_cnt):
        """
        set ACPR meas average count.
        :param i_cnt:
        :return:
        """
        str_cmd = ":ACP:AVER:COUN"
        self.write(str_cmd + " {0}".format(i_cnt))
        if float(self.inst.query(str_cmd + "?")) == i_cnt:
            self.logger.debug("Set ACRP Average Cnt:{0} Success".format(i_cnt))
            return True
        else:
            self.logger.error("Set ACRP Average Cnt:{0} Fail".format(i_cnt))
            return False

    def set_acpr_avg_onoff(self, i_onoff):
        """
        set ACPR meas average on or off.
        :param i_onoff:1 for ON, 0 for OFF
        :return:
        """
        str_cmd = ":ACP:AVER"

        self.write(str_cmd + " {0}".format(i_onoff))
        if float(self.inst.query(str_cmd + "?")) == i_onoff:
            self.logger.debug("Set ACRP Average MODE:{0} Success".format(i_onoff))
            return True
        else:
            self.logger.error("Set ACRP Average MODE:{0} Fail".format(i_onoff))
            return False

    def set_acpr_ref_level(self, i_level):
        """
        Set Ref Level
        :param i_level: Y Level  ,dBm
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_ref_level(i_level)

        if i_level > 20:
            i_level = 20
        self.write(":DISP:ACP:VIEW:WIND:TRAC:Y:RLEV {0}dBm".format(i_level))
        ret_lvl = self.get_acpr_ref_level()
        if fabs(ret_lvl - i_level) < 1:
            self.logger.debug("Set ACP Ref Level {0} Success".format(i_level))
            return True
        else:
            self.logger.error("Set ACP Ref Level {0} Fail".format(i_level))
            return False

    def get_acpr_ref_level(self):
        ret_lvl = float(self.inst.query(":DISP:ACP:VIEW:WIND:TRAC:Y:RLEV?"))
        self.logger.debug("Get ACP Ref Level {0}dBm".format(ret_lvl))
        return ret_lvl

    def set_acpr_trace_type(self, i_type):
        """
        set ACPR Trace Type..
        No much use.
        :param i_type: 0,WRITe;
                        1, AVERage;
                        2, MAXHold;
                        3, MINHold
        :return:
        """

        if self.inst_model == _E4445A:
            return True

        str_cmd = ":TRAC:ACP:TYPE"
        str_cmd_type = str()
        if i_type == 0:
            str_cmd_type = "WRIT"
        elif i_type == 1:
            str_cmd_type = "AVER"
        elif i_type == 2:
            str_cmd_type = "MAXH"
        elif i_type == 3:
            str_cmd_type = "MINH"

        self.write(str_cmd + " {0}".format(str_cmd_type))
        if str(self.inst.query(str_cmd + "?")).count(str_cmd_type) != 0:
            self.logger.debug("Set ACPR Trace Type:{0} Success".format(str_cmd_type))
            return True
        else:
            self.logger.error("Set ACPR Trace Type:{0} Fail".format(str_cmd_type))
            return False

    def meas_acpr(self, i_offset_cnt=2):
        """
        Set ACPR meas off count .
        :param i_offset_cnt:
        :return:
        """
        self.write(":INIT:CONT ON")
        if self.inst_model == _N9010:
            self.write(":INIT:ACP")
            cmd_str = ":READ:ACP1?"
            acpr = self.inst.query_ascii_values(cmd_str)
        else:
            cmd_str = ":READ:ACP?;*WAI;"
            acpr = self.inst.query_ascii_values(cmd_str)

        ret_list = list()
        offset = int()
        if i_offset_cnt == 1:
            offset = 1
        elif i_offset_cnt == 2:
            offset = 4
        for x in xrange(i_offset_cnt * 2):
            ret_list.append(acpr[offset + i_offset_cnt * x])
        return ret_list

    def set_obw_span(self, f_span):
        """
        Set OBW meas Span,,,It need to be config at last
        :param f_span:KHz
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_span(f_span)

        str_cmd = ":OBW:FREQ:SPAN"
        self.write(str_cmd + " {0}KHz".format(f_span))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_span:
            self.logger.debug("Set OBW Span:{0}KHz Success".format(f_span))
            return True
        else:
            self.logger.error("Set OBW Span:{0}KHz Fail".format(f_span))
            return False

    def set_obw_rbw(self, f_rbw):
        """
        Set OBW Rbw
        :param f_rbw:KHz
        :return:
        """
        if self.inst_model == _E4445A:
            str_cmd = ":BWID:RES"
        else:
            str_cmd = ":OBW:BAND"
        self.write(str_cmd + " {0}KHz".format(f_rbw))

        if float(self.inst.query(str_cmd + "?")) / 1000 == f_rbw:
            self.logger.debug("Set OBW RBW:{0}KHz Success".format(f_rbw))
            return True
        else:
            self.logger.error("Set OBW RBW:{0}KHz Fail".format(f_rbw))
            return False

    def set_obw_ref_level(self, i_level):
        """
        Set Ref Level
        :param i_level: Y Level  ,dBm
        :return:
        """
        if self.inst_model == _E4445A:
            return self.set_ref_level(i_level)

        if i_level > 20:
            i_level = 20
        self.write(":DISP:OBW:VIEW:WIND:TRAC:Y:RLEV {0}dBm".format(i_level))
        ret_lvl = self.get_obw_ref_level()
        if fabs(ret_lvl - i_level) < 1:
            self.logger.debug("Set OBW Ref Level {0} Success".format(i_level))
            return True
        else:
            self.logger.error("Set OBW Ref Level {0} Fail".format(i_level))
            return False

    def get_obw_ref_level(self):
        ret_lvl = float(self.inst.query(":DISP:OBW:VIEW:WIND:TRAC:Y:RLEV?"))
        self.logger.debug("Get OBW Ref Level {0}dBm".format(ret_lvl))
        return ret_lvl

    def set_obw_trace_type(self, i_type):
        """
        set OBW Trace Type..
        No much use.
        :param i_type: 0,WRITe;
                        1, AVERage;
                        2, MAXHold;
                        3, MINHold
        :return:
        """
        if self.inst_model == _E4445A:
            str_cmd = ":SENS:OBW:MAXH"
            if i_type == 0:
                str_cmd_type = "OFF"
                query_str = "0"
            elif i_type == 2:
                str_cmd_type = "ON"
                query_str = "1"
            else:
                self.logger.debug("E4445A Not Support")
                return False

            self.write(str_cmd + " {0}".format(str_cmd_type))
            if str(self.inst.query(str_cmd + "?")).count(query_str) != 0:
                self.logger.debug("Set OBW Trace Type:MAXH {0} Success".format(str_cmd_type))
                return True
            else:
                self.logger.error("Set OBW Trace Type:MAXH {0} Fail".format(str_cmd_type))
                return False
        else:
            str_cmd = ":TRAC:OBW:TYPE"
            str_cmd_type = str()
            if i_type == 0:
                str_cmd_type = "WRIT"
            elif i_type == 1:
                str_cmd_type = "AVER"
            elif i_type == 2:
                str_cmd_type = "MAXH"
            elif i_type == 3:
                str_cmd_type = "MINH"
            self.write(str_cmd + " {0}".format(str_cmd_type))

            if str(self.inst.query(str_cmd + "?")).count(str_cmd_type) != 0:
                self.logger.debug("Set OBW Trace Type:{0} Success".format(str_cmd_type))
                return True
            else:
                self.logger.error("Set OBW Trace Type:{0} Fail".format(str_cmd_type))
                return False

    def meas_obw(self):
        """
        measure obw
        :return: KHz
        """
        self.write(":INIT:CONT ON")
        if self.inst_model == _N9010:
            self.write(":INIT:OBW")
        obw = self.inst.query(":READ:OBW:OBW?")
        return float(obw) / 1000

    def set_marker_mode(self, i_no=1, i_mode=0):
        """

        :param i_no:
        :param i_mode:1,POSition,2,DELTa,3,FIXed,3,OFF
        :return:
        """
        str_cmd = ":CALC:MARK{0}:STAT".format(i_no)
        self.write(str_cmd + " 1")
        if float(self.inst.query(str_cmd + "?")) == 1:
            self.logger.debug("Marker{0} set state ON Success".format(i_no))
        else:
            self.logger.error("Marker{0} set state ON Fail".format(i_no))
            return False

        str_cmd_type = ""
        if i_mode == 0:
            return True
        elif i_mode == 1:
            str_cmd_type = "POS"
        elif i_mode == 2:
            str_cmd_type = "DELT"
        elif i_mode == 3:
            str_cmd_type = "FIX"
        elif i_mode == 4:
            str_cmd_type = "OFF"

        str_cmd = ":CALC:MARK{0}:MODE {1}".format(i_no, str_cmd_type)
        self.write(str_cmd)
        if str(self.inst.query(":CALC:MARK{0}:MODE?".format(i_no))).count(str_cmd_type) != 0:
            self.logger.debug("Marker{0} set Mode {1} Success".format(i_no, str_cmd_type))
        else:
            self.logger.error("Marker{0} set Mode {1} Fail".format(i_no, str_cmd_type))
            return False
        sleep(0.05)
        return True

    def marker_peak_search(self, i_no=1):
        """

        :param i_no:
        :return:
        """
        self.write(":CALC:MARK:PEAK:SEAR:MODE MAX")
        ret = self.inst.query(":CALC:MARK:PEAK:SEAR:MODE?")
        if ret.count("MAX") == 0:
            self.logger.error("Set Peak Search mode Fail")
            return False
        # sleep(0.05)
        str_cmd = ":CALC:MARK{0}:MAX".format(i_no)
        self.write(str_cmd)
        self.logger.debug("Peak Search success")
        return True

    def set_marker_x(self, x_val, i_no=1):
        """
        Set Marker x Value in KHz
        :param i_no: the Marker No.
        :param x_val: the Value KHz
        :return:
        """
        self.write(":CALC:MARK{0}:X {1}KHz".format(i_no, x_val))
        if self.get_marker_x_val(i_no) == x_val:
            self.logger.debug("Set Marker X Value to {0}KHz Success".format(x_val))
            return True
        else:
            self.logger.error("Set Marker X Value to {0}KHz Fail".format(x_val))
            return False

    def get_marker_y_val(self, i_no=1):
        """
        get marker y value
        :param i_no:
        :return: db Value
        """
        ret = float(self.inst.query(":CALC:MARK{0}:Y?".format(i_no)))
        return ret

    def get_marker_x_val(self, i_no=1):
        """
        get marker x value
        :param i_no:
        :return: KHz
        """
        ret = float(self.inst.query(":CALC:MARK{0}:X?".format(i_no))) / 1000
        return ret

    def set_trace_type(self, i_type):
        str_cmd_type = str()
        if i_type == 0:
            str_cmd_type = "WRIT"
        elif i_type == 1:
            str_cmd_type = "AVER"
        elif i_type == 2:
            str_cmd_type = "MAXH"
        elif i_type == 3:
            str_cmd_type = "MINH"

        self.write(":TRAC:MODE {0}".format(str_cmd_type))
        ret_mode = str(self.inst.query("TRAC:MODE?"))
        if ret_mode.count(str_cmd_type) != 0:
            self.logger.debug("Config to {0} Mode Success".format(str_cmd_type))
            return True
        else:
            self.logger.error("Config to {0} Mode Fail".format(str_cmd_type))
            return False

    def reset_sa(self):
        """
        Reset SA
        :return:
        """
        self.write("*CLS")
        self.write("*RST")
        if self.isopen:
            self.set_cont_mode(1)
        return True

    def check_align(self):
        """
        Set Align.auto CAL
        :return:
        """
        self.write(":CAL")
        while True:
            try:
                self.inst.query("*OPC?")
            except VisaIOError:
                pass
            else:
                self.logger.debug("Align Finish")
                break

        return True

    def set_marker_disable(self):
        """
        Set all marker off
        :return:
        """
        self.write(":CALC:MARK:OFF")
        self.logger.debug("Set All Marker OFF")
        return True

    def meas_amplitude(self, f_cent, f_span, f_rbw, i_atten, i_reflevel, f_avg_cnt):
        pass


if __name__ == '__main__':
    sa = SA()
    sa.open_sa()
    sa.reset_sa()
    # sa.conf_meas_mode(2)
    # sa.set_obw_trace_type(2)
    # sa.set_timeout(2000)
    # sa.conf_meas_mode(0)
    sa.set_cent_freq(922625)
    # sa.set_span(500)
    # sa.set_rbw(4.7)
    # sa.set_avg_count(100)
    # sa.set_input_atten(20)
    #
    sa.conf_meas_mode(1)
    sa.set_cent_freq(922625)
    sa.set_acpr_sweep(500)
    sa.set_acpr_space(0.075)
    sa.set_acpr_rbw(2.4)
    sa.set_vbw(24)
    sa.set_acpr_carr_cnt(1)
    sa.set_acpr_carr_band(250)
    sa.set_acpr_offset_freq([250, 500])
    sa.set_acpr_ch_bw([250, 250])
    sa.set_acpr_avg_cnt(5)
    sa.set_acpr_span(2000)
    try:
        print(sa.meas_acpr())
    except VisaIOError:
        pass

    #
    # sa.conf_meas_mode(2)
    # sa.set_cent_freq(922625)
    # sa.set_obw_rbw(47)
    # sa.set_obw_span(1000)
    # sa.set_sweep_time(500)
    # sa.set_obw_trace_type(2)
    # sa.set_obw_ref_level(20)
    # sleep(3)
    # print sa.meas_obw()
    # sa.set_obw_trace_type(0)
    #
    # sa.check_align()
    # sa.conf_meas_mode(0)
    # sa.set_trace_type(0)
    # sa.set_marker_disable()
    # sa.set_input_atten(30)
    # sa.set_cent_freq(922625)
    # sa.set_span(500)
    # sa.set_rbw(4.7)
    # sa.set_marker_mode(1, 1)
    # sa.marker_peak_search(1)
    # sleep(1)
    # power = sa.get_marker_y_val()
    # print str(sa.get_marker_x_val()) + "KHz"
    # print str(power) + "dB"
    # sa.set_ref_level(power + 7)
    sa.close_sa()
