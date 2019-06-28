import pigpio

class GHLamps(object):
    """A container class to access the IoT Greenhouse lamps.
    """
    red = None
    white = None
    dual = None

    def __init__(self, pi, red_led_gpio, white_led_gpio, dual_led_gpio1, dual_led_gpio2):
        """Initializes a container for IoT Greenhouse lamps
        
        :param pi: reference to pigpio service
        :param red_led_gpio: GPIO port for red LED. Use GHgpio definitions.
        :param white_led_gpio: GPIO port for white LED. Use GHgpio definitions.
        :param dual_led_gpio1: GPIO port for dual LED pin 1. Use GHgpio definitions.
        :param dual_led_gpio2: GPIO port for dual LED pin 2. Use GHgpio definitions.
        :returns: GHLamps object
        """
        self.red = GHLamp(pi, red_led_gpio)
        self.white =  GHLamp(pi, white_led_gpio)
        self.dual = GHLampDual(pi, dual_led_gpio1, dual_led_gpio2)


class GHLamp(object):
    """A class to access IoT Greenhouse LED lamp.
    """   
    LAMP_ON = False #active low
    LAMP_OFF = True

    def __init__(self, pi, gpio):
        """Initializes an IoT Greenhouse lamp.
        
        :param pi: reference to pigpio service
        :param gpio: GPIO port for LED. Use GHgpio definitions.
        :returns: GHLamp object
        """
        self._pi = pi
        self._gpio = gpio
        self._pi.set_mode(self._gpio, pigpio.OUTPUT) 
        self._pi.write(self._gpio, self.LAMP_OFF)

    def on(self):
        """Activate lamp.
        """
        self._pi.write(self._gpio, self.LAMP_ON)
    
    def off(self):
        """Deactivate lamp.
        """
        self._pi.write(self._gpio, self.LAMP_OFF)

    def toggle(self):
        """Toggle lamp state.
        """
        if self.is_on():
            self.off()
        else:
            self.on()

    def get_state(self):
        """Returns current state of lamp.
        """
        return self._pi.read(self._gpio)
    
    def is_on(self):
        """Returns Boolean indicating lamp is on.
        """
        return self.get_state() == self.LAMP_ON

    def is_off(self):
        """Returns Boolean indicating lamp is off.
        """
        return self.get_state() == self.LAMP_OFF
    
    def get_status(self):
        """Gets status of lamp.

        :returns: Lamp status as string.
        """
        if self.is_on():
            return "ON"
        else:
            return "OFF"
            

class GHLampDual(object):
    """A class to access the IoT Greenhouse dual color lamp.
    """   
    LAMP_OFF = 0
    LAMP_ON_YELLOW = 1
    LAMP_ON_GREEN = 2

    _pi = None
    _shared_gpio1 = 0
    _gpio2 = 0
    _state = LAMP_OFF

    def __init__(self, pi, shared_gpio1, gpio2):
        """Initializes an IoT Greenhouse dual lamp.
        
        :param pi: reference to pigpio service
        :param shared_gpio1: GPIO port 1 for Dual LED. Currently shared with RED LED.
        :param gpio2: GPIO port 2 for Dual LED. 
        :returns: GHLampDual object
        """
        self._pi = pi
        self._shared_gpio1 = shared_gpio1
        self._gpio2 = gpio2
        self._pi.set_mode(self._shared_gpio1, pigpio.OUTPUT)   
        self._pi.set_mode(self._gpio2, pigpio.INPUT) 
        self._pi.write(self._shared_gpio1, True)
        
        self._state = self.LAMP_OFF

    def on_green(self):
        """Activates dual lamp as green.
        """
        self._pi.set_mode(self._gpio2, pigpio.OUTPUT)
        self._pi.write(self._shared_gpio1, False)
        self._pi.write(self._gpio2, True)
        self._state = self.LAMP_ON_GREEN

    def on_yellow(self):
        """Activates dual lamp as yellow.
        """
        self._pi.set_mode(self._gpio2, pigpio.OUTPUT)
        self._pi.write(self._shared_gpio1, True)
        self._pi.write(self._gpio2, False)
        self._state = self.LAMP_ON_YELLOW

    def off(self):
        """Deactivates dual lamp.
        """
        self._pi.set_mode(self._gpio2, pigpio.INPUT)
        self._state = self.LAMP_OFF

    def get_state(self):
        """Returns current state of dual lamp

        :returns: GHLampDual.LAMP_ON_GREEN, GHLampDual.LAMP_ON_YELLOW, or GHLampDual.LAMP_OFF
        """
        return self._state

    def is_green(self):
        """Returns Boolean indicating lamp is green.
        """
        return self.get_state() == self.LAMP_ON_GREEN

    def is_yellow(self):
        """Returns Boolean indicating lamp is yellow.
        """
        return self.get_state() == self.LAMP_ON_YELLOW

    def is_off(self):
        """Returns Boolean indicating lamp is off.
        """
        return self.get_state() == self.LAMP_OFF

    def get_status(self):
        """Gets status of dual lamp.

        :returns: Button status as string.
        """
        if self.is_green():
            return "GREEN"
        if self.is_yellow():
            return "YELLOW"
        else:
            return "OFF"