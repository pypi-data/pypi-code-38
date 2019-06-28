import pigpio

class GHFan(object):
    """A class to access the IoT Greenhouse fan.
    """
    
    FAN_ON = True
    FAN_OFF = False

    def __init__(self, pi, fan_gpio):
        """Initializes the IoT Greenhouse fan.
        
        :param pi: reference to pigpio service
        :param fan_gpio: GPIO port for fan. Use GHgpio definitions.
        :returns: GHFan object
        """
        self._pi = pi
        self._gpio = fan_gpio
            
        self._pi.set_mode(self._gpio, pigpio.OUTPUT)        
        #Fan off
        self._pi.write(self._gpio, self.FAN_OFF)
        
    def on(self):
        """Activates the fan.
        """
        self._pi.write(self._gpio, self.FAN_ON)
        
    def off(self):
        """Deactivates the fan.
        """
        self._pi.write(self._gpio, self.FAN_OFF)
    
    def toggle(self):
        """Toggle fan state.
        """
        if self.is_on():
            self.off()
        else:
            self.on()

    def get_state(self):
        """Returns the current state of the fan.
        """
        return self._pi.read(self._gpio)

    def is_on(self):
        """Returns Boolean indicating fan is on.
        """
        return self.get_state() == self.FAN_ON

    def is_off(self):
        """Returns Boolean indicating fan is off.
        """
        return self.get_state() == self.FAN_OFF
    
    def get_status(self):
        """Gets status of fan.

        :returns: Fan status as string.
        """
        if self.get_state() == self.FAN_ON:
            return "ON"
        else:
            return "OFF"