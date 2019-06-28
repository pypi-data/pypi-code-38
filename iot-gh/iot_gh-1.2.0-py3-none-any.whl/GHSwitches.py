from time import sleep
import pigpio

class GHSwitches(object):
    """A container class to access the IoT Greenhouse switches.
    """
   
    def __init__(self, pi, pb_switch_gpio, toggle_switch_gpio):
        """Initializes a container for IoT Greenhouse switches.
    
        Returns references to both push button and toggle switches

        :param pi: reference to pigpio service
        :param pb_switch_gpio: GPIO port for push button switch. Use GHgpio definitions.
        :param toggle_switch_gpio: GPIO port for toggle switch. Use GHgpio definitions.
        :returns: GHSwitches object
        """
        self.push_button = GHSwitch(pi, pb_switch_gpio)
        self.toggle = GHSwitch(pi, toggle_switch_gpio)

class GHSwitch(object):
    """A class to access IoT Greenhouse switch.
    """  
    SWITCH_ON = False
    SWITCH_OFF = True
       
    def __init__(self, pi, switch_gpio):
        """Initializes an IoT Greenhouse switch.
        
        Returns references to switch object. Used for both push button and toggle.

        :param pi: reference to pigpio service
        :param switch_gpio: GPIO port for switch. Use GHgpio definitions.
        :returns: GHSwitch object
        """
        self._pi = pi
        self._gpio = switch_gpio
        self._pi.set_mode(self._gpio, pigpio.INPUT)        
        
    def get_state(self, debounce=False):
        """Returns current state of switch. 
        """
        if not debounce:
            return self._pi.read(self._gpio)
        else:
            first_read = False
            second_read = True
            debouce_delay = .01
            while first_read != second_read:
                first_read = self._pi.read(self._gpio)
                sleep(debouce_delay)
                second_read = self._pi.read(self._gpio)
            return first_read

    def wait_for_press(self):
        """Waits for switch on or switch pressed state.
        """
        while self.get_state():
            sleep(.2)

    def wait_for_release(self):
        """Waits for switch off or switch released state.
        """
        while not self.get_state():
            sleep(.2)

    def wait_for_press_and_release(self):
        """Waits for switch press and released states.
        """
        self.wait_for_press()
        self.wait_for_release()

    def is_on(self):
        """Returns Boolean indicating switch is on.
        """
        return self.get_state() == GHSwitch.SWITCH_ON

    def is_off(self):
        """Returns Boolean indicating switch is off.
        """
        return self.get_state() == GHSwitch.SWITCH_OFF

    def get_status(self):
        """Gets status of switch.

        :returns: Switch status as string.
        """
        if self.get_state() == GHSwitch.SWITCH_ON:
            return "ON"
        else:
            return "OFF"