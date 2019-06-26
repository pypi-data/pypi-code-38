import pigpio
import time
from . import DHT11
from . import DHT22



class DHT:
    def __init__(self, sensor_type, pin):
        self.pi = pigpio.pi()
        self.pin = pin
        self.sensor_type = sensor_type
        if self.sensor_type == 11:
            self.sensor = DHT11.DHT11(self.pi, self.pin)
        if self.sensor_type == 22:
            self.sensor = DHT22.sensor(self.pi, self.pin)

    def read(self):
        if self.sensor_type == 11:
            self.sensor.read()
        if self.sensor_type == 22:
            self.sensor.trigger()
        time.sleep(0.2)
        temp = 0
        humid = 0
        if self.sensor_type == 11:
            temp = self.sensor.temperature
            humid = self.sensor.humidity
        if self.sensor_type == 22:
            temp = self.sensor.temperature()
            humid = self.sensor.humidity()
        return {'temperature':temp, 'humidity':humid}

    def stop(self):
        if self.sensor_type == 11:
            self.sensor.close()
        if self.sensor_type == 22:
            self.sensor.cancel()
        self.pi.stop()


    #def __del__(self):
    #    self.stop()
