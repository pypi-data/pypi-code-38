# -*- coding: utf-8 -*-

"""package fft_dev
brief     Handle 3562A device through GPIB-Ethernet adapter.
author    Benoit Dubois
copyright FEMTO Engineering, 2019
licence   GPL 3.0+
"""

import logging
import socket
import struct
import numpy as np
from time import sleep
from iopy.prologix import PrologixGpibEth


FUNCTION_MAPPING = {
    1: "Frequency response",
    2: "Power spectrum 1",
    3: "Power spectrum 2",
    5: "Cross spectrum",
    6: "Input time 1",
    7: "Input time 2"}

CHANNEL_MAPPING = {
    0: "Channel 1",
    1: "Channel 2",
    2: "Channel 1 and Channel 2"}

DOMAIN_TYPE_MAPPING = {
    0: "Time",
    1: "Frequency",
    3: "Voltage (amplitude)"}

VOLT_MAPPING = {
    0: "Peak",
    1: "RMS",
    2: "Indicates peak only"}

YAXIS_UNIT_MAPPING = {
    0: "Volts",
    1: "Volts^2",
    2: "PSD (Volts^2/Hz)",
    3: "ESD (Volts^2s/Hz)",
    4: "sqrt-PSD (Volts/sqrt-Hz)",
    5: "None",
    6: "Volts",
    7: "Volts^2"}

XAXIS_UNIT_MAPPING = {
    0: "None",
    1: "Hertz",
    2: "RPM",
    3: "Orders",
    4: "Seconds",
    5: "Revs",
    6: "Degrees",
    7: "dB",
    8: "dBV",
    9: "Volts"}

MODE_MAPPING = {
    0: "Linear resolution",
    1: "Log resolution",
    2: "Swept sine",
    3: "Time Capture",
    4: "Linear resolution throughput"}


# =============================================================================
class FftParam(object):
    """FftParam class, a container for FFT acquisition parameters.
    """

    def __init__(self):
        """Constructor.
        :returns: None
        """
        self.function = None
        self.n_elts = None
        self.d_elts = None
        self.channels = None
        self.domain = None
        self.volt = None
        self.unity = None
        self.unitx = None
        self.is_float = None
        self.is_complex = None
        self.is_log = None
        self.mode = None
        self.rfs = None
        self.ifs = None
        self.dx = None
        self.average = None
        self.sfreq = None
        self.decades = None

    def __str__(self):
        """Return string representation of the instance of the class.
        :returns: String representation of the instance (str)
        """
        # Function
        if self.function in FUNCTION_MAPPING is True:
            retval = "Function: " + FUNCTION_MAPPING[self.function] + "\n"
        else:
            retval = "Function: code number " + str(self.function) + "\n"
        # Number of elements
        retval += "Data contains " + str(self.n_elts) + \
            " elements among which " + str(self.d_elts) + " are displayed\n"
        # Channel selection
        if self.channels in CHANNEL_MAPPING is True:
            retval += "Channel selected: " + CHANNEL_MAPPING[self.channels] \
                + "\n"
        else:
            retval += "No channel selected\n"
        # Domain type
        if self.domain in DOMAIN_TYPE_MAPPING is True:
            retval += "Domain type: " + DOMAIN_TYPE_MAPPING[self.domain] + "\n"
        else:
            retval += "Domain type: bad index " + str(self.domain) + "\n"
        # Volts peak/rms
        if self.volt in VOLT_MAPPING is True:
            retval += "Volt: " + VOLT_MAPPING[self.volt] + "\n"
        else:
            retval += "Volts: bad index " + str(self.volt) + "\n"
        # Y axis units
        if self.unity in YAXIS_UNIT_MAPPING is True:
            retval += "Y-axis units: " + YAXIS_UNIT_MAPPING[self.unity] + "\n"
        else:
            retval += "Y-axis units: bad unit y" + str(self.unity) + "\n"
        # X axis units
        if self.unitx in XAXIS_UNIT_MAPPING is True:
            retval += "X-axis units: " + XAXIS_UNIT_MAPPING[self.unitx] + "\n"
        else:
            retval += "X-axis units: bad unit x " + str(self.unitx) + "\n"
        # Data format
        retval += "Data type is float: " + str(self.is_float) + "\n"
        retval += "Data type is complex: " + str(self.is_complex) + "\n"
        retval += "Log data: " + str(self.is_log) + "\n"
        # Measurement mode
        if self.mode in MODE_MAPPING is True:
            retval += "Measurement mode: " + MODE_MAPPING[self.mode] + "\n"
        else:
            retval += "Measurement mode: unexpected mode " + str(self.mode) \
              + "\n"
        # Sampling frequency/2 (real)
        retval += "Sampling frequency/2 (real): {:.0f}\n".format(self.rfs)
        # Sampling frequency/2 (imag)
        retval += "Sampling frequency/2 (imag): {:.0f}\n".format(self.ifs)
        # Delta X-axis^2 (delta frequency or time)
        retval += "Delta X-axis^2: {:.6f}\n".format(self.dx)
        # Number of averaging
        retval += "Number of average: {:.0f}\n".format(self.average)
        # Start frequency
        retval += "Measurement starts at: " + str(self.sfreq) + " Hz\n"
        # Number of decades
        retval += "Measurement mades on " + str(self.decades) + " decades\n"
        # Return string representation
        return retval


# =============================================================================
class FftStream(object):
    """FftStream class, a container for FFT acquisition data stream.
    """

    def __init__(self, rawdata=None):
        """Constructor.
        :param rawdata: Raw data readed from device (str)
        :returns: None
        """
        if rawdata is None:
            raise ValueError("Argument rawdata missing")
        if rawdata.find(b'#I') == 0:  # ASCII message
            rawdata = rawdata.replace(b'#I', b'')
            arawdata = np.fromstring(rawdata, dtype=np.float32, sep='\n')[1:]
        elif rawdata.find(b'#A') == 0:  # TODO: ANSI message or Binary message
            rawdata = rawdata.replace(b'#A', b'')
            s = struct.Struct('>H')
            nb_elem = int(s.unpack(rawdata[0:2])[0] / 8)
            s = struct.Struct('>' + nb_elem*'d')
            arawdata = np.asarray(s.unpack(rawdata[2:]))
        else:  # TODO: Binary message
            raise ValueError("FFT stream misformed")
        self.param = self._process_header(arawdata[0:66])
        self.ydata = self._build_ydata(arawdata[66:])
        self.xdata = self._build_xdata()

    @staticmethod
    def _process_header(data):
        """Extracts informations about acquisition from data header returned by
        device (see table 3-3 and 3-3 page 38-39).
        :param data: data returned by device (array)
        :returns: parameters of acquisition (FftParam)
        """
        if data[1] == 0:
            logging.error("No data transfered, abort.")
            raise
        acq_param = FftParam()
        # Display function
        acq_param.function = data[0]
        # Number of elements
        acq_param.n_elts = data[1]
        # Displayed elements
        acq_param.d_elts = data[2]
        # Number of average
        acq_param.average = data[3]
        # Channel selection
        acq_param.channels = data[4]
        # Domain type
        acq_param.domain = data[7]
        # Volts peak/rms
        acq_param.volt = data[8]
        # Y axis units
        acq_param.unity = data[9]
        # X axis units
        acq_param.unitx = data[10]
        # Data format
        if data[35] == 0:
            acq_param.is_float = False
        else:
            acq_param.is_float = True
        if data[36] == 0:
            acq_param.is_complex = False
        else:
            acq_param.is_complex = True
        if data[40] == 0:
            acq_param.is_log = False
        else:
            acq_param.is_log = True
        # Measurement mode
        acq_param.mode = data[43]
        # Sampling frequency/2 (real)
        acq_param.rfs = data[52]
        # Sampling frequency/2 (imag)
        acq_param.ifs = data[53]
        # Delta X-axis^2 (delta frequency or time)
        acq_param.dx = data[55]
        # Start frequency
        acq_param.sfreq = data[64]
        # Number of decades
        acq_param.decades = int(acq_param.n_elts/80)
        #
        return acq_param

    def _build_xdata(self):
        """Builds ordona data.
        :returns: vector of data representing abscissa (np.array)
        """
        if self.param.is_log is False:  # linear data
            xdata = np.linspace(
                start=self.param.sfreq,
                stop=self.param.sfreq + self.param.n_elts * self.param.dx,
                num=self.param.n_elts,
                endpoint=False)
        else:  # log data
            idx = np.reshape(np.arange(self.param.n_elts), (1, -1)).T
            pts_dec = 1 / self.param.dx
            xdata = self.param.sfreq * np.power(10.0, idx/pts_dec)
        return xdata

    def _build_ydata(self, data):
        """Builds ordinate data(s).
        :param data: array of value (np.array)
        :returns: vector of data representing ordinate (np.array)
        """
        if self.param.function == 1:  # Frequency Response
            real = data[::2]
            imag = data[1::2]
            mag = 20 * np.log10(np.sqrt(np.power(real, 2) + np.power(imag, 2)))
            phy = 180 / np.pi * np.arctan(imag/real)
            ydata = np.asarray([real, imag, mag, phy]).T
        elif self.param.function == 2 or self.param.function == 3:  # Pow Spec
            ydata = 10 * np.log10(data[:])
            ydata = np.reshape(ydata, (1, -1)).T
        elif self.param.function == 5:  # Cross Spectrum
            real = np.reshape(data[::2], (1, -1)).T
            imag = np.reshape(data[1::2], (1, -1)).T
            cspec = 10 * np.log10(
                np.power((np.power(real, 2) + np.power(imag, 2)), 0.5))
            ydata = np.concatenate((real, imag, cspec), axis=1)
        else:
            ydata = np.reshape(data[:], (1, -1)).T
        return ydata


# =============================================================================
class Fft3562aDevPrologix(PrologixGpibEth):
    """3562A_prologix class, handle FFT device through GPIB-Ethernet adapter
    from Prologix.
    """

    def __init__(self, ip, port, gpib_addr):
        """Constructor.
        :returns: None
        """
        super().__init__(ip, port, gpib_addr)

    def connect(self):
        """Initialization process:
        - init Prologix
        - clear HPIB interface
        :returns: None
        """
        super().init()

    def clear_hpib_interface(self):
        """Clear the HPIP interface (see p.8 of programming guide).
        :returns: None
        """
        self.write("CLEAR {}".format(self.gpib_addr))
        sleep(1)

    def reset_3562(self):
        """Reset for 3562A analyzer.
        :returns: None
        """
        self.write("RST")
        sleep(1)

    def get_id(self):
        """Returns identification string of device.
        :returns: identification string of device (str)
        """
        self.write("ID?")
        try:
            _id = self.read(100, 0.5)
        except socket.timeout:
            pass
        return _id

    def dump_data_state(self):
        """Acquires internal state of FFT analyzer.
        Data are transfered from device in ASCII format.
        :returns: Data representing state of analyzer (str)
        """
        logging.info("Dump device state")
        try:
            self.write("DSAS")  # Dump State in AScii command
            state = ''
            try:
                while True:  # Read until all data transfered
                    state += self.read(1024, 1.0)
            except socket.timeout:
                pass
        except KeyboardInterrupt:
            logging.info("State dump stopped by user")
            raise
        except socket.error as er:
            logging.error("Socket error during state dump: %r", er)
            raise
        except Exception as er:
            logging.error("Unexpected exception during state dump: %r", er)
            raise
        logging.info("Dump --> Ok")
        return state

    def dump_data_trace(self):
        """Acquires data trace displayed on FFT analyzer. Data are transfered
        from device in ANSI format.
        :returns: Data representing active trace on analyzer display (str)
        """
        logging.info("Dump data trace")
        try:
            # self.write("DDAN")  # TODO: Dump Data in ANsi
            # trace = bytes()
            self.write("DDAS")  # Dump Data in ASci
            trace = ''
            try:
                while True:  # Read until all data transfered
                    trace += self.read(4096, 1.0)
            except socket.timeout:
                pass
        except KeyboardInterrupt:
            logging.info("Data trace dump stopped by user")
            raise
        except socket.error as er:
            logging.error("Socket error during data trace dump: %r", er)
            raise
        except Exception as er:
            logging.error("Unexpected error during data trace dump: %r", er)
            raise
        logging.info("Dump --> Ok")
        return trace.encode('utf-8')

    @staticmethod
    def scale_data(data, data_range):
        """Scale data with the formula (see p.57 of programming guide):
            scaled_data = -4/3 * data * data_range * 32768 / 26028.55
        which can be simplified for implementation in the folowing manner:
            scaled_data = -131072 / 78085.65 * data * data_range
        :param data: array of value (np.array)
        :param data_range: range setting for the channel (float)
        :reeturns: scaled data value (np.array)
        """
        scaled_data = -131072 / 78085.65 * data * data_range
        return scaled_data

    def dump_time_capture(self):
        """Acquire time capture file of FFT analyzer (ie raw data).
        Data are transfered from device in ANSII format.
        For more informations, see p.67 3562A programming guide.
        :returns: Time capture from analyzer (str)
        """
        logging.info("Dump time capture")
        try:
            # self.write("DBAN")  # TODO: Dump Blocks in ANsi
            self.write("DBAS")  # Dump Blocks in AScii
            dump = ''
            try:
                while True:  # Read until all data transfered
                    dump += self.read(8192, 2.0)
            except socket.timeout:
                pass
        except KeyboardInterrupt:
            logging.info("Dump stopped by user")
            return
        except socket.error as er:
            logging.error("Socket error during dump: %r", er)
            raise
        except Exception as er:
            logging.error("Unexpected exception during dump: %r", er)
            raise
        logging.info("Dump --> Ok")
        return dump
