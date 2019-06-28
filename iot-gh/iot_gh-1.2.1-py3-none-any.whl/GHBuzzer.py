from time import sleep
import pigpio

class GHBuzzer(object):
    """A class to access the IoT Greenhouse buzzer.
    """
    BUZZER_ON = False
    BUZZER_OFF = True
    BEEP_DELAY_ON = .5
    BEEP_DELAY_OFF = .3

    def __init__(self, pi, buzzer_gpio):
        """Initializes an IoT Greenhouse buzzer.
        
        :param pi: Reference to pigpio service.
        :param buzzer_gpio: GPIO port for buzzer. Use GHgpio definitions.
        :returns: GHBuzzer object
        """
        self._pi = pi
        self._gpio = buzzer_gpio

        self._pi.set_mode(self._gpio, pigpio.OUTPUT)        
        #buzzer off
        self._pi.write(self._gpio, self.BUZZER_OFF)
        
    def on(self):
        """Activate buzzer.
        """
        self._pi.write(self._gpio, self.BUZZER_ON)

    def off(self):
        """Deactivate buzzer.
        """
        self._pi.write(self._gpio, self.BUZZER_OFF)

    def beep(self, duration = BEEP_DELAY_ON):
        """Activates buzzer for specifed duration.
        
        :param duration float: Number of seconds to activate buzzer.
        """
        self.on()
        sleep(duration)
        self.off()
 
    def beeps(self, duration = BEEP_DELAY_ON, beep_count = 2):
        """Activates buzzer for multiple beeps.

        :param duration float: Number of seconds to sound buzzer.
        :param beep_count int: Number of times to beep.
        """
        for i in range(0, beep_count):
            if i > 0:
                sleep(self.BEEP_DELAY_OFF)
        self.beep(duration)
            
    def get_state(self):
        """Returns current state of buzzer.
        """
        return self._pi.read(self._gpio)

    def is_on(self):
        """Returns Boolean indicating buzzer is on.
        """
        return self.get_state() == self.BUZZER_ON

    def is_off(self):
        """Returns Boolean indicating buzzer is off
        """
        return self.get_state() == self.BUZZER_OFF

    def get_status(self):
        """Gets status of buzzer.

        :returns: Button status as string.
        """
        if self.get_state() == self.BUZZER_ON:
            return "ON"
        else:
            return "OFF"