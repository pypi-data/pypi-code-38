#import spidev
import time
import os

class GHAnalogService(object):
    """A container class to access IoT Greenhouse analog channels

    Provides collection of 8 A/D inputs based on channel definitions.
    """
    # Define sensor channels
    POT_CHANNEL  = 0
    LIGHT_CHANNEL  = 1
    TEMP_CHANNEL = 2
    AUX_CHANNEL = 3
    AD_IN_4_CHANNEL = 4
    AD_IN_5_CHANNEL = 5
    AD_IN_6_CHANNEL = 6
    AD_IN_7_CHANNEL = 7

    def __init__(self, pi, spi):
        """Provides access to IoT Greenhouse analog channels
        
        :param pi pigpio.pi: Reference to current pigpio service
        :param spi spidev.spi: Reference to spi object
        :returns: AnalogService container object
        """
        self._pi = pi
        # Open SPI bus
        self._spi = spi #spidev.SpiDev()
        self._spi.open(0,0)
        self._spi.max_speed_hz=1000000
        
        self.pot = GHAnalogChannel(self._spi, self.POT_CHANNEL)
        self.light = GHAnalogChannel(self._spi, self.LIGHT_CHANNEL)
        self.temp = GHAnalogChannel(self._spi, self.TEMP_CHANNEL)
        self.aux = GHAnalogChannel(self._spi, self.AUX_CHANNEL)
        self.ad_in_4 = GHAnalogChannel(self._spi, self.AD_IN_4_CHANNEL)
        self.ad_in_5 = GHAnalogChannel(self._spi, self.AD_IN_5_CHANNEL)
        self.ad_in_6 = GHAnalogChannel(self._spi, self.AD_IN_6_CHANNEL)
        self.ad_in_7 = GHAnalogChannel(self._spi, self.AD_IN_7_CHANNEL)
 
 
class GHAnalogChannel(object):
    """A class to access analog channels. Provides get functions to 
    read both raw digital and voltage values.
    """
    
    def __init__(self, spi, channel):
        """Initializes an analog channel.
        
        :param spi spidev.spi: Reference to spi object
        :param channel int: Channel index for this channel
        :returns: GHAnalogChannel service for specified channel
        """
        self._spi = spi  
        self._channel = channel
        
    def get_value(self):
        """Gets raw digital value for this analog channel
        
        :return: Digital value of analog channel
        """
        adc = self._spi.xfer2([1,(8+self._channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data

    # rounded to specified number of decimal places.
    def get_voltage(self, places = 1):
        """Gets voltage value for this analog channel
        
        :param places int: Number of places to round to. Default is 1.
        :return: Voltage value of analog channel
        """
        data = self.get_value()   
        volts = (data * 3.3) / float(1023)
        volts = round(volts, places)
        return volts

