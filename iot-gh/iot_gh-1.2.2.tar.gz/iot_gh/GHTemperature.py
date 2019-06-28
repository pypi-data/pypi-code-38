import threading
from time import sleep

class GHTemperature(object):
    """A class to read IoT Greenhouse temperature.
    """
 
    def __init__(self, analog_temp_channel_in, analog_temp_channel_out):
        """Initializes an IoT Greenhouse temperature service.
        
        Wrapper class for analog temperature channels
        :param analog_temp_channel_in: reference to inside temperature analog channel
        :param analog_temp_channel_out: reference to outside temperature analog channel
        :returns: GHTemperature object
        """
        self._analogTempSensor_in = analog_temp_channel_in
        self._analogTempSensor_out = analog_temp_channel_out
        

    def convert_C_to_F(self, temp_C):
        """Converts Celsius to Fahrenheit.
        """
        return temp_C * 9/5 +32

    def convert_F_to_C(self, temp_F):
        """Converts Fahrenheit to Celsius.
        """
        return (temp_F - 32) * 5/9

    # Function to calculate temperature in C from LM35 data
    def _convert_to_temp(self, data):
        """Converts A/D data to temp C.
        """
        temp = ((data * 330)/float(1023))
        return temp

    def get_inside_temp_C(self):
        """Gets inside temperature in degrees C.
        """
        analog_value = self._analogTempSensor_in.get_value()
        temp_value_C = self._convert_to_temp(analog_value)
        return round(temp_value_C, 1)

    def get_inside_temp_F(self):
        """Gets inside temperature in degrees F.
        """
        temp_value_F = self.convert_C_to_F(self.get_inside_temp_C()) 
        return round(temp_value_F, 1)

    def get_outside_temp_C(self):
        """Gets outside temperature in degrees C.
        """
        analog_value = self._analogTempSensor_out.get_value()
        temp_value_C = self._convert_to_temp(analog_value)
        return round(temp_value_C, 1)

    def get_outside_temp_F(self):
        """Gets outside temperature in degrees F.
        """
        temp_value_F = self.convert_C_to_F(self.get_outside_temp_C()) 
        return round(temp_value_F, 1)
