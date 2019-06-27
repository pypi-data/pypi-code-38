# -*- coding: utf-8 -*-

"""package fft_dev
brief     Handle 35670A device through GPIB-Ethernet adapter.
author    Benoit Dubois
copyright FEMTO Engineering, 2019
licence   GPL 3.0+
"""

import logging
import socket
import array
from time import sleep
import numpy as np

from iopy.prologix import PrologixGpibEth

LOG_FREQ_START_MAP = {
    "10 mHz": 15.625e-3,
    "100 mHz": 93.75e-3,
    "1 Hz": 1,
    "10 Hz": 10,
    "100 Hz": 100,
    "1 kHz": 1e3,
    "10 kHz": 10e3}

LOG_FREQ_STOP_MAP = {
    "100 mHz": 210.9375e-3,
    "1 Hz": 1.578125,
    "10 Hz": 10,
    "100 Hz": 100,
    "1 kHz": 1e3,
    "10 kHz": 10e3,
    "100 kHz": 115.025e3}

AVERAGE_TYPE_MAP = {
    "Maximum": "MAX",
    "RMS": "RMS",
    "Time": "TIME",
    "Vector": "VECT",
    "EConfidence": "ECON"}

AVERAGE_NUMBER_LIMITS = (1, 9999999)

MAJOR_MODE_MAP = {
    "FFT Analysis": "FFT",
    # "Order Analysis": "ORD",  # Option 1D0
    # "Octave Analysis": "OCT",  # Option 1D1
    # "Swept Sine": "SINE",  # Option 1D2
    "Histogram": "HIST",
    "Correlation Analysis": "CORR"}

MEASUREMENT_LIST = (
    "Auto correlation",
    "Capture buffer",
    "Coherence",
    "Composite Power",
    "Cross Correlation",
    "Cross Spectrum",
    "Cumulative Density Function",
    "Data Register",
    "Frequency Response",
    "Histogram",
    "Linear Spectrum",
    "Normalized Variance",
    "Orbit Diagram",
    "Order Track",
    "Power spectrum",
    "Probability Density Function",
    "RPM Profile",
    "Time",
    "Unfiltered Time",
    "Waterfall Register",
    "Windowed Time")

FFT_MEASUREMENT_MAP = {
    "Capture buffer": "TCAP {:1d}",
    "Coherence": "XFR:POW:COH {:1d},{:1d}",
    "Cross Spectrum": "XFR:POW:CROS {:1d},{:1d}",
    "Data Register": "D{:1d}",
    "Frequency Response": "XFR:POW:RAT {:1d},{:1d}",
    "Linear Spectrum": "XFR:POW:LIN {:1d}",
    "Orbit Diagram": "XVOL:VOLT {:1d},{:1d}",
    "Power spectrum": "XFR:POW {:1d}",
    "Time": "XTIM:VOLT {:1d}",
    "Waterfall Register": "W{:1d}",
    "Windowed Time": "XTIM:VOLT:WIND {:1d}"}

DOMAIN_TYPE_MAP = {
    "Time": 0,
    "Frequency": 1,
    "Voltage (amplitude)": 3}

VOLT_MAP = {
    "Peak": 0,
    "RMS": 1,
    "Indicates peak only": 2}

YAXIS_UNIT_AMPLITUDE_MAP = {
    "Peak amplitude": "PEAK",
    "Peak to peak amplitude": "PP",
    "RMS amplitude": "RMS"}

YAXIS_FORMAT_MAP = {
    "Linear magnitude": "MLIN",
    "Log magnitude": "MLOG",
    "Phase": "PHAS",
    "Unwrapped phase": "UPH",
    "Real part": "REAL",
    "Imaginary part": "IMAG",
    "Nyquist diagram": "NYQ",
    "Polar diagram": "POL",
    "Group delay": "GDEL"}

YAXIS_UNIT_MAP = {
    "Volts": "\"V\"",
    "Volts^2": "\"V2\"",
    "PSD (V^2/Hz)": "\"V2/HZ\"",
    "ESD (V^2s/Hz)": "\"V2S/HZ\"",
    "sqrt-PSD (V/sqrt(Hz))": "\"V/RTHZ\""}

XAXIS_UNIT_MAP = {
    # "None": "",
    "Hertz": "\"HZ\"",
    "RPM": "\"RPM\"",
    "Orders": "\"ORD\""}
# "Seconds": "\"HZ\""}
# "Revs",
# "Degrees",
# "dB",
# "dBV",
# "Volts"}

INPUT_COUPLING = {"DC": "DC",
                  "AC": "AC"}

INPUT_IMPEDANCE = {"Float (1 Mohms)": "FLO",
                   "Ground (55 ohms)": "GRO"}

SOURCE_SHAPE_MAP = {
    "Random": "RAND",
    "Burst random": "BRAN",
    "Sinusoid": "SIN",
    "Periodic chirp": "PCH",
    "Burst chirp": "BCH",
    "Pink": "PINK"}
# "USER": "Arbitrary",  # with option 1D4
# "CAPT": "Capture"}    # with option 1D4

SOURCE_LEVEL_VRMS_LIMITS = (-9.9e37, 13.9794)

SOURCE_OFFSET_LIMITS = (-10.0, 10.0)


# =============================================================================
class Fft35670aDevPrologix(PrologixGpibEth):
    """35670A_prologix class, handle FFT device through GPIB-Ethernet adapter
    from Prologix. Reference to page or table in the documentation refere to
    the "GPIB Programming with the Agilent 35670A" book.
    """

    def connect(self):
        """Initialization process:
        - init Prologix
        :returns: None
        """
        return super().init()

    def clear_hpib_interface(self):
        """Clear the HPIP interface.
        :returns: None
        """
        self.write("*CLS")
        sleep(1)

    def reset(self):
        """Reset for 35670A analyzer.
        :returns: None
        """
        self.write("*RST")
        sleep(6)

    @property
    def idn(self):
        """Returns identification string of device.
        :returns: identification string of device (str)
        """
        self.write("*IDN?")
        try:
            return self.read(256, 0.5)[:-1]
        except socket.timeout:
            logging.warning("Socket timeout when querying ID")
            return ""

    def get_major_mode(self):
        """p.13-3
        """
        self.write("INST:SEL?")
        return self.read(256, 0.8)[:-1].replace('\"', '')

    def set_major_mode(self, mode):
        if mode not in MAJOR_MODE_MAP.values():
            raise ValueError("Bad major mode query: %r", mode)
        self.write("INST:SEL {}", mode)

    def set_measurement(self, meas, trace_nb=1):
        """Set the measurement data to be displayed in the specified trace
        (p.6-23). The available measurement data varies for different
        instrument modes.
        See table 6-2 for a complete listing of measurement results and
        their related <CMDSTR> for each instrument mode.
        :param meas: measurement type (str)
        :param trace_nb: number of the trace (int)
        :returns: None
        """
        self.write("CALC{:1d}:FEED {}".format(trace_nb, meas))

    def get_measurement(self, trace_nb=1):
        """Get the measurement data to be displayed in the specified trace
        (p.6-23).
        :param trace_nb: number of the trace (int)
        :returns: measurement type (str)
        """
        self.write("CALC{:1d}:FEED?".format(trace_nb))
        return self.read(256)[:-1].replace('\"', '')

    def get_averaging_state(self):
        """p.18-12
        """
        self.write("AVER:STAT?")
        return True if '1' in self.read(32, 0.8) else False

    def set_averaging_state(self, state=False):
        if state is False:
            state = 0
        else:
            state = 1
        self.write("AVER:STAT {}".format(state))

    def get_averaging_nb(self):
        """p.18-3
        """
        self.write("AVER:COUN?")
        return int(self.read(1024, 0.8)[:-1])

    def set_averaging_nb(self, count):
        self.write("AVER:COUN {:d}".format(count))

    def get_averaging_type(self):
        """p.18-19
        """
        self.write("AVER:TYPE?")
        return self.read(128, 0.8)[:-1]

    def set_averaging_type(self, type_):
        if type_ not in AVERAGE_TYPE_MAP.values():
            raise ValueError("Bad averaging type query")
        self.write("AVER:TYPE {}".format(type_))

    def get_source_state(self):
        """Get internal source state (p.16-3).
        :returns: state of output (bool)
        """
        self.write("OUTP:STAT?")
        return False if "+0" in self.read(256)[:-1] else True

    def set_source_state(self, state):
        """Set internal source state (p.16-3).
        :param state: state of output (bool)
        :returns: None
        """
        if state is True:
            self.write("OUTP:STAT ON")
        else:
            self.write("OUTP:STAT OFF")

    def get_source_shape(self):
        """Get internal source function shape (p.19-5).
        :returns: source shape (str)
        """
        self.write("SOUR:FUNC:SHAP?")
        return self.read(256)[:-1]

    def set_source_shape(self, shape):
        """Set internal source function shape (p.19-5).
        :param shape: function shape of source (str)
        :returns: None
        """
        if shape not in SOURCE_SHAPE_MAP.values():
            raise ValueError("Bad source shape query: %r", shape)
        self.write("SOUR:FUNC:SHAP {}".format(shape))

    def get_source_level(self):
        """Get output level of internal source (in volt) (p.19-10)
        :returns: output level of source (float)
        """
        self.write("SOUR:VOLT:AMPL?")
        retval = self.read(256)[:-1]
        return float(retval)

    def set_source_level(self, level):
        """Set output level of internal source (in volt) (p.19-10)
        :param level: output level of source (float)
        :returns: None
        """
        if level < SOURCE_LEVEL_VRMS_LIMITS[0]:
            level = SOURCE_LEVEL_VRMS_LIMITS[0]
        if level > SOURCE_LEVEL_VRMS_LIMITS[-1]:
            level = SOURCE_LEVEL_VRMS_LIMITS[-1]
        self.write("SOUR:VOLT:AMPL {:.4e} VRMS".format(level))

    def get_source_offset(self):
        """Get DC offset of internal source (in volt) (p.19-11)
        :returns: DC offset of source (float)
        """
        self.write("SOUR:VOLT:OFFS?")
        return float(self.read(1024)[:-1])

    def set_source_offset(self, offset):
        """Set DC offset of internal source (+-10 volt) (p.19-11)
        :param offset: DC offset of source (float)
        :returns: None
        """
        if offset < SOURCE_OFFSET_LIMITS[0]:
            offset = SOURCE_OFFSET_LIMITS[0]
        if offset > SOURCE_OFFSET_LIMITS[-1]:
            offset = SOURCE_OFFSET_LIMITS[-1]
        self.write("SOUR:VOLT:OFFS {:.4e}".format(offset))

    def get_resolution_mode(self):
        self.write("SENS:FREQ:RES:AUTO?")
        return self.read(1024)[:-1]

    def set_resolution_mode(self, mode):
        """p.18-34 Default auto mode is ON.
        """
        self.write("SENS:FREQ:RES:AUTO {:d}".format(mode))

    def data_type(self, type_):
        if type_ == "REAL":
            self.write("FORM:DATA:REAL")
        else:
            self.write("FORM:DATA:ASCII")

    def get_data_range(self, tcap):
        self.write("SENS:DATA:RANGE? TCAP{:d}".format(tcap))
        return self.read(1024)[:-1]

    def set_data_range(self, tcap, range_):
        self.write("SENS:DATA:RANGE TCAP{:d} {}".format(tcap, range_))

    def get_input_state(self, inp):
        """Get one-channel, two-channel or four-channel measurements state
        (p.12-9).
        :param inp: number of the specified input (int)
        :returns: state of the specified input (bool)
        """
        self.write("INP{:1d}:STATe?".format(inp))
        return True if '1' in self.read(64) else False

    def set_input_state(self, inp, state):
        """Specify one-channel, two-channel or four-channel measurements
        (p.12-9). To select a two-channel measurement, send INP2 ON.
        With Option AY6, send 'INP2 ON;:INP4 OFF'. To select a one-channel
        measurement, send 'INP2 OFF'. The analyzer takes data from Channel 1
        only. To select a four-channel measurement (only available with
        Option AY6), send 'INP4 ON'.
        :param inp: number of the specified input (int)
        :param state: state of the specified input (bool)
        :returns:
        """
        if state is True:
            self.write("INP{:1d}:STATe ON".format(inp))
        else:
            self.write("INP{:1d}:STATe OFF".format(inp))

    def get_input_coupling(self, inp):
        """Get AC or DC coupling for the specified channel (p.12-3)
        :param inp: number of the specified input (int)
        :returns: 'AC' or 'DC' (str)
        """
        self.write("INP{:1d}:COUP?".format(inp))
        return self.read(256)[:-1]

    def set_input_coupling(self, inp, coupling):
        """Select AC or DC coupling for the specified channel (p.12-3)
        :param inp: number of the specified input (int)
        :param coupling: 'AC' or 'DC' (str)
        :returns: None
        """
        if coupling is "AC":
            self.write("INP{:1d}:COUP AC".format(inp))
        else:
            self.write("INP{:1d}:COUP DC".format(inp))

    def get_input_impedance(self, inp):
        """Get the specified channel’s input shield (float or ground).
        (p.12-6)
        :param inp: number of the specified input (int)
        :returns: 'GRO' or 'FLO' (str)
        """
        self.write("INP{:1d}:LOW?".format(inp))
        return self.read(256)[:-1].replace('\"', '')

    def set_input_impedance(self, inp, imp):
        """Set the specified channel’s input shield to float or to ground.
        (p.12-6)
        :param inp: number of the specified input (int)
        :param imp: 'GROund' or 'FLOat' (str)
        :returns: None
        """
        if 'FLO' in imp:
            self.write("INP{:1d}:LOW FLOAT".format(inp))
        else:
            self.write("INP{:1d}:LOW GROUND".format(inp))

    def get_input_autorange_state(self, inp):
        """Get input autorange state (p.518 (18-79)).
        :param inp: number of the specified input (int)
        :returns: true if autorange is on else false (bool)
        """
        self.write("SENS:VOLT{:1d}:DC:RANG:AUTO?".format(inp))
        return False if "+0" in self.read(256)[:-1] else True

    def set_input_autorange_state(self, inp, state):
        """Set input autorange state (p.518 (18-79)).
        :param inp: number of the specified input (int)
        :param state: true if autorange is on else false (bool)
        :returns: None
        """
        if state is True:
            self.write("SENS:VOLT{:1d}:DC:RANG:AUTO ON".format(inp))
        else:
            self.write("SENS:VOLT{:1d}:DC:RANG:AUTO OFF".format(inp))

    def get_overload_reject_state(self):
        """Get input overload reject state (p.498 (18-59)).
        :returns: true if overload reject is on else false (bool)
        """
    
        self.write("SENS:REJ:STAT?")
        return False if "+0" in self.read(256)[:-1] else True

    def set_overload_reject_state(self, state):
        """Set input overload reject state (p.498 (18-59)).
        :param state: true if overload reject is on else false (bool)
        :returns: None
        """
        if state is True:
            self.write("SENS:REJ:STAT ON")
        else:
            self.write("SENS:REJ:STAT OFF")

    def points(self, trace_nb=1):
        # self.write("SENS:DATA:POIN? TCAP{:d}".format(tcap))
        self.write("CALC{:1d}:DATA:HEAD:POIN?".format(trace_nb))
        return self.read(512)[:-1]

    def set_xspace(self, space, trace_nb=1):
        """Specifies a linear or logarithmic scale for the X-axis
        data spacing (p.6-108). Required 1D3 option.
        :param space:  X-axis scaling 'LIN' or 'LOG' (str)
        :param trace_nb: number of the trace (int)
        :returns: None
        """
        self.write("CALC{:1d}:SYNT:SPAC {}".format(trace_nb, space))

    def get_xspace(self, trace_nb=1):
        """Returns scale (linear or logarithmic) for the X-axis
        data spacing (p.6-108). Required 1D3 option.
        :param trace_nb: number of the trace (int)
        :returns: X-axis scaling 'LIN' or 'LOG' (str)
        """
        self.write("CALC{:1d}:SYNT:SPAC?".format(trace_nb))
        return self.read(64)[:-1].replace('\"', '')

    def set_xspace_display(self, space, trace_nb=1):
        """Specify X-axis scaling (linear or logarithmic) on display (p.8-33).
        Omit the specifier or send 1 for trace A, 2 for trace B, 3 for trace C,
        or 4 for trace D.
        :param space: X-axis scaling 'LIN' or 'LOG' (str)
        :param trace_nb: number of the trace to acquire (int)
        returns: None
        """
        self.write("DISP:WIND{:1d}:TRAC:X:SPAC {}".format(trace_nb, space))

    def get_xspace_display(self, trace_nb=1):
        """Return X-axis scaling (linear or logarithmic) on display (p.8-33).
        Omit the specifier or send 1 for trace A, 2 for trace B, 3 for trace C,
        or 4 for trace D.
        :param trace_nb: number of the trace to acquire (int)
        returns: X-axis scaling 'LIN' or 'LOG' (str)
        """
        self.write("DISP:WIND{:1d}:TRAC:X:SPAC?".format(trace_nb))
        return self.read(64)[:-1].replace('\"', '')

    def set_xunit(self, unit, trace_nb=1):
        """Specify the X-axis unit (p.3-121).
        :param unit: X axis unit 'HZ', 'CPM', 'ORD' or 'USER' (str)
        :param trace_nb: number of the trace (int)
        returns: None
        """
        self.write("CALC{:1d}:UNIT:X {}".format(trace_nb, unit))

    def get_xunit(self, trace_nb=1):
        """Get the X-axis unit (p.3-121).
        :param trace_nb: number of the trace (int)
        returns: X axis unit 'HZ', 'CPM', 'ORD' or 'USER' (str)
        """
        self.write("CALC{:1d}:UNIT:X?".format(trace_nb))
        return self.read(512)[:-1].replace('\"', '')

    def set_yspace_display(self, space, trace_nb=1):
        """Specify Y-axis scaling (linear or logarithmic) of display (p.8-42).
        Omit the specifier or send 1 for trace A, 2 for trace B, 3 for trace C,
        or 4 for trace D.
        :param space: Y-axis scaling 'LIN' or 'LOG' (str)
        :param trace_nb: number of the trace to acquire (int)
        returns: None
        """
        self.write("DISP:WIND{:1d}:TRAC:Y:SPAC {}".format(trace_nb, space))

    def get_yspace_display(self, trace_nb=1):
        """Return Y-axis scaling (linear or logarithmic) of display (p.8-42).
        Omit the specifier or send 1 for trace A, 2 for trace B, 3 for trace C,
        or 4 for trace D.
        :param trace_nb: number of the trace to acquire (int)
        returns: Y-axis scaling 'LIN' or 'LOG' (str)
        """
        self.write("DISP:WIND{:1d}:TRAC:Y:SPAC?".format(trace_nb))
        return self.read(64)[:-1].replace('\"', '')

    def set_yunit(self, unit, trace_nb=1):
        """Selects the vertical unit for the specified display’s Y-axis
        (p.6-119).
        :param unit: 'V'|'V2'|'V/RTHZ'|'V2/HZ'|'V2S/HZ' (str)
        :param trace_nb: number of the trace (int)
        returns: None
        """
        self.write("CALC{:1d}:UNIT:VOLT {}".format(trace_nb, unit))

    def get_yunit(self, trace_nb=1):
        """Selects the vertical unit for the specified display’s Y-axis
        (p.6-119).
        :param trace_nb: number of the trace (int)
        returns: 'V'|'V2'|'V/RTHZ'|'V2/HZ'|'V2S/HZ' (str)
        """
        self.write("CALC{:1d}:UNIT:VOLT?".format(trace_nb))
        return self.read(512)[:-1].replace('\"', '')

    def set_yunitamplitude(self, uamp, trace_nb=1):
        """Select the unit of amplitude for the Y-axis scale (P. 6-111).
        :param uamp: Y axis unit of amplitude PEAK, PP or RMS (str)
        :param trace_nb: number of the trace (int)
        returns: None
        """
        self.write("CALC{:1d}:UNIT:AMPL {}".format(trace_nb, uamp))

    def get_yunitamplitude(self, trace_nb=1):
        """Get the unit of amplitude for the Y-axis scale (P. 6-111).
        :param trace_nb: number of the trace (int)
        returns: Y axis unit of amplitude PEAK, PP or RMS (str)
        """
        self.write("CALC{:1d}:UNIT:AMPL?".format(trace_nb))
        return self.read(512)[:-1].replace('\"', '')

    def set_yformat(self, format_, trace_nb=1):
        """Select a coordinate system for displaying measurement data and
        for transferring coordinate transformed data to a controller (p.6-29)
        :param format_: MLIN|MLOG|PHAS|REAL|IMAG|NYQ|UPH|GDEL|POL (str)
        :param trace_nb: number of the trace (int)
        returns: None
        """
        self.write("CALC{:1d}:FORM {}".format(trace_nb, format_))

    def get_yformat(self, trace_nb=1):
        """Get the coordinate system for displaying measurement data and
        for transferring coordinate transformed data to a controller (p.6-29)
        :param trace_nb: number of the trace (int)
        returns: MLIN|MLOG|PHAS|REAL|IMAG|NYQ|UPH|GDEL|POL (str)
        """
        self.write("CALC{:1d}:FORM?".format(trace_nb))
        return self.read(256)[:-1].replace('\"', '')

    def set_dbref_lvl(self, value, trace_nb=1):
        """Set dB magnitude reference level
        :param value: new value (float)
        :param trace_nb: number of the trace (int)
        returns: None
        """
        self.write("CALC{:1d}:UNIT:DBR {}".format(trace_nb, value))

    def get_dbref_lvl(self, trace_nb=1):
        """Get dB magnitude reference level
        :param trace_nb: number of the trace (int)
        returns: db magnitude reference level value (float)
        """
        self.write("CALC{:1d}:UNIT:DBR?".format(trace_nb))
        return float(self.read(256)[:-1])

    def get_freq_start(self):
        self.write("SENS:FREQ:START?")
        return float(self.read(256)[:-1])

    def set_freq_start(self, freq):
        self.write("SENS:FREQ:START {}".format(freq))

    def get_freq_stop(self):
        self.write("SENS:FREQ:STOP?")
        return float(self.read(512)[:-1])

    def set_freq_stop(self, freq):
        self.write("SENS:FREQ:STOP {}".format(freq))

    def get_freq_span(self):
        self.write("SENS:FREQ:SPAN?")
        return float(self.read(512, 0.8)[:-1])

    def set_freq_span(self, span):
        """p.18-40
        """
        self.write("SENS:FREQ:SPAN {:f}".format(span))

    def get_freq_resolution(self):
        """p.18-31
        """
        self.write("SENS:FREQ:RES?")
        return int(self.read(512, 0.8)[:-1])

    def set_freq_resolution(self, res=400):
        """p.18-31
        FFT mode:
        Resolution |     baseband    |       zoom
                   |  freq  |  time  |  freq  | complex time
        ------------------------------------------------------
            100    |   101  |  256   |   101  |   128
            200    |   201  |  512   |   201  |   256
            400    |   401  |  1024  |   401  |   512
            800    |   801  |  2048  |   801  |   1024

        Swept mode:
             FREQ:RES:AUTO:MIN       |  Number of displayed points
          Number of measured points  |
        ------------------------------------------------------------
             3 to 401 PNT/SWP        |         401
            402 to 801 PNT/SWP       |         801
        """
        self.write("SENS:FREQ:RES {}".format(res))

    def get_blocksize(self):
        self.write("SENS:FREQ:BLOC?")
        return int(self.read(1024, 0.8)[:-1])

    def set_blocksize(self, number="", step="", bound=""):
        """p. 18-27
        FFT mode:
         Block  |     Baseband    |       Zoom
         Size   |       freq      |  freq  | complex time
        ----------------------------------------------------
         256    |       101       |   101  |    128
         512    |       201       |   201  |    256
         1024   |       401       |   401  |    512
         2048   |       801       |   801  |    1024

        Correlation mode:
         Block  |     Auto and Cross correlation
         Size   | 0 to T/2 | -T/2 to T/2 | -T/4 to T/4
        ----------------------------------------------------
         256    |   128    |     256     |    128
         512    |   256    |     512     |    256
         1024   |   512    |     1024    |    512
         2048   |   1024   |     2048    |    1024
        """
        if number != "":
            msg = number
        if step != "":
            msg = step
        if bound != "":
            msg = bound
        self.write("SENS:FREQ:BLOC {}".format(msg))

    def time_spacing(self):
        start_freq = self.start_freq
        stop_freq = self.stop_freq
        spacing = 400 / (stop_freq - start_freq)
        return spacing

    def acquisition(self, flag):
        """Query device to proceed to a new acquisition and wait until
        completion of operation.
        :param flag:
        :returns: None
        """
        logging.info("Start acquisition")
        self.write("ABOR;:INIT:IMM;*OPC")
        opc = 0
        try:
            while (opc & 1) == 0 and flag.is_set() is True:
                self.write("*ESR?")
                opc = self.read(8, 1.5)
                if opc is None:
                    opc = 0
                else:
                    opc = int(opc)
                sleep(0.5)
        except Exception as ex:
            logging.error("%r", ex)
            return False
        #
        self.write(":INIT:CONT OFF")
        logging.info("--> acquisition finished")
        return True

    def _get_bin_data(self):
        """Basic binary data acquisition process.
        !!! To be used after a data query !!!
        :returns: Data  (array of float)
        """
        try:
            nb_byte_digit = int(self.read(2, 1.0)[1:2])
            nb_byte = int(self.read(nb_byte_digit, 1.0))
        except Exception as er:
            logging.error("Error while reading data header: %r", er)
            raise
        rawdata = bytes()
        try:
            # Use of 'while len(rawdata) < nb_byte:' cause unexpected error
            # when reading data, so we read until all data transfered and
            # the end of transfert is signaled with a timeout on data read.
            while True:
                rawdata += self.raw_read(256, 4.0)
        except socket.timeout:
            if len(rawdata[:-1]) == nb_byte:
                logging.info("End of binary data dump")
            else:
                logging.warning("Socket timeout during data dump")
                raise socket.timeout
        except socket.error as ex:
            logging.warning("Socket error during data dump: %r", ex)
            raise ex
        except KeyboardInterrupt:
            logging.info("Data dump stopped by user")
            raise KeyboardInterrupt
        except Exception as ex:
            logging.error("Unexpected exception during data dump: %r", ex)
            raise ex
        data = array.array("d", rawdata[:-1])  # Array of double
        data.byteswap()
        return data

    def get_ydata(self, trace_nb=1):
        """Get 'y' data. Data are transfered in binary format.
        Note that device acquisition must be stopped before getting data.
        :param trace_nb: number of the trace to acquire (int)
        :returns: Data array (array of float)
        """
        logging.info("Dump 'y' data of trace %d", trace_nb)
        self.write("FORM:DATA REAL, 64")
        self.write("CALC{:1d}:DATA?".format(trace_nb))
        data = self._get_bin_data()
        logging.info("Dump 'y' data --> Ok")
        return data

    def get_xdata(self, trace_nb=1):
        """Get 'x' data. Data are transfered in binary format.
        :param trace_nb: number of the trace to acquire (int)
        :returns: Data array (array of float)
        """
        logging.info("Dump 'x' data of trace %d", trace_nb)
        self.write("FORM:DATA REAL, 64")
        self.write("CALC{:1d}:X:DATA?".format(trace_nb))
        data = self._get_bin_data()
        logging.info("Dump 'x' data --> Ok")
        return data


# =============================================================================
def main_bin(dev):
    """Example script.
    """

    trace_nb = 1

    try:
        ret = dev.connect()
        if ret is None:
            return [], []
        print("id:", dev.idn)
        dev.write("*CLS")
        dev.write("INP2 OFF")

        idx_f_min = 6
        idx_f_max = 7
        freq_range_list = [(list(LOG_FREQ_START_MAP.values())[x-1],
                            list(LOG_FREQ_STOP_MAP.values())[x-1])
                           for x in range(idx_f_max, idx_f_min, -1)]
        ydata = array.array("d")
        xdata = array.array("d")
        for f_start, f_stop in freq_range_list:
            # Set analysis frequency band
            dev.set_freq_start(f_start)
            dev.set_freq_stop(f_stop)
            dev.acquisition()
            # Get new 'y' then 'x' data
            new_y = dev.get_ydata(trace_nb)
            new_x = dev.get_xdata(trace_nb)[:len(new_y)]
            # Collect data being aware to duplicate frequency band
            idx = np.searchsorted(xdata, new_x[-1], side='left')
            ydata = new_y + ydata[idx:]
            xdata = new_x + xdata[idx:]
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        return None, None
    except Exception as ex:
        logging.error("Exception: %r", ex)
        raise

    return xdata, ydata


# =============================================================================
if __name__ == "__main__":
    # For "Ctrl+C" works
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    import matplotlib.pyplot as plt

    # Handles log
    DATE_FMT = "%d/%m/%Y %H:%M:%S"
    LOG_FORMAT = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.INFO,
                        datefmt=DATE_FMT,
                        format=LOG_FORMAT)

    GPIB_ADDR = 11
    IP = '192.168.0.52'
    PORT = 1234

    DEV = Fft35670aDevPrologix(IP, PORT, GPIB_ADDR)

    DEV.connect()
    DEV.set_source_state(True)
    DEV.set_source_shape("RAND")
    DEV.set_source_offset(0.0)
    DEV.set_source_level(1.0)

    XDATA, YDATA = main_bin(DEV)
    if XDATA is not None:
        plt.plot()
        plt.grid(which='minor', axis='x', linewidth=0.5)
        plt.grid(which='major', axis='y', linewidth=0.5)
        plt.loglog(XDATA, YDATA, 'blue')
        plt.xlabel("f (Hz)")
        plt.ylabel("Magnitude (dB)")
        plt.show()
