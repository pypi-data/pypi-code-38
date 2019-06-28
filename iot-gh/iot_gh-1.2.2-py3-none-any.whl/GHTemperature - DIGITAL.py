import threading
from time import sleep
#from GH.dht11 import DHT11 #Current config is using two analog sensors

class GHTemperature(threading.Thread):
    """This class GHFan provides a services to control the IoT Greenhouse fan
    """
    
    _analogTempSensor_in = None
    _analogTempSensor_out = None
#    _digitalTempSensor = None

    inside_temp_C = 0
    inside_temp_F = 0
    outside_temp_C = 0
    outside_temp_F = 0
 #   humidity = 0
    reading_is_valid = False
    last_valid_read = 0

    def __init__(self, analog_temp_channel_in, analog_temp_channel_out):
        self._digitalTempSensor = DHT11(digital_pin)
        self._analogTempSensor = analog_temp_channel
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        #get inside temp and humidity
        result = self._digitalTempSensor.read()
        if result.is_valid():
            self.reading_is_valid = True
            self.last_valid_read = datetime.datetime.now()
            self.inside_temp_C = result.temperature
            self.inside_temp_F = convert_C_to_F(self.inside_temp_C)
            self.humidity = result.humidity
        #get outside temp
        analog_value = self._analogTempSensor.get_value()
        self.outside_temp_C = self._convert_to_temp(analog_value, 1)
        self.outside_temp_F = self.convert_C_to_F(self.outside_temp_C) 
        
        sleep(1)


    def convert_C_to_F(self, temp_C):
        return temp_C * 9/5 +32

    def convert_F_to_C(self, temp_F):
        return (temp_F - 32) * 5/9

    # Function to calculate temperature from
    # TMP36 data, rounded to specified
    # number of decimal places.
    def _convert_to_temp(self, data, places):
 
      # ADC Value
      # (approx)  Temp  Volts
      #    0      -50    0.00
      #   78      -25    0.25
      #  155        0    0.50
      #  233       25    0.75
      #  310       50    1.00
      #  465      100    1.50
      #  775      200    2.50
      # 1023      280    3.30
 
      temp = ((data * 330)/float(1023))-50
      temp = round(temp,places)
      return temp
