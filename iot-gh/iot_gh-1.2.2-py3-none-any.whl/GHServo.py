from time import sleep
import pigpio
from iot_gh.GHgpio import GHgpio

class GHServo(object):
    """A class to access the IoT Greenhouse servo.
    """    
    FREQ = 50
    PERIOD = 1/FREQ
    CCW_PW_LIMIT = 2000
    CW_PW_LIMIT = 500
    
    def __init__(self, pi, servo_gpio,  cw_position, ccw_position):
        """Initializes the IoT Greenhouse servo.
        
        :param pi: reference to pigpio service
        :param servo_gpio: GPIO PWM port for servo. Must be hardware PWM pin
        :param ccw_position: Counter-clockwise pulse width in microseconds
        :param cw_position: Clockwise pulse width in microseconds
        :returns: GHServo object
        """
        #cw and ccw position in microseconds
        if cw_position < self.CW_PW_LIMIT:
            raise ValueError("Error: CW position value must be between greater than %i" % self.CW_PW_LIMIT)
        elif cw_position > self.CCW_PW_LIMIT:
            raise ValueError("Error: CW position value must be between less than %i" % self.CCW_PW_LIMIT)
        if servo_gpio != 18:
            raise ValueError("Error: Only GPIO18 currently supported.")
  
        self._pi = pi
        self._gpio = servo_gpio  
        self._ccw_pulse_width = ccw_position
        self._cw_pulse_width = cw_position
        self._center_pulse_width = (cw_position + ccw_position)//2        
        
        #pi.hardware_PWM(self._gpio, self.FREQ, 250000) # 800Hz 25% dutycycle
        self._position = 0
        dc = self._calc_duty_cycle(self._calc_pulse_width(self._position))
        self._pi.hardware_PWM(self._gpio, self.FREQ, dc)       
        
    def _calc_pulse_width(self, position):
        if position < 0 or position > +1:
            raise ValueError("Error: Servo position is specified between 0 (full CCW) and 1 (full CW).")
        
        pw = self._ccw_pulse_width - position * (self._ccw_pulse_width - self._cw_pulse_width)
        return pw

    def _calc_duty_cycle(self, pulse_width):
        if pulse_width < self._cw_pulse_width or pulse_width > self._ccw_pulse_width:
            raise ValueError("Error: Servo pulse width is specified between %i (full CCW) and %i (full CW)." % (self._ccw_pulse_width, self._cw_pulse_width))
        
        dc = int(pulse_width/self.PERIOD)
        return dc

    def move(self, position=0):
        """ Normalized move method with 0 being max left (ccw) and +1 being max right (cw)
        
        :param position: Normalized position value between 0 and +1.0.
        """
        if position < 0 or position > 1:
            raise Exception("Error: Position values must be between 0 and 1.0.")
        else:
            self._position = position
            dc = self._calc_duty_cycle(self._calc_pulse_width(self._position))
            self._pi.hardware_PWM(self._gpio, self.FREQ, dc)       

    def is_ccw(self):
        """Returns Boolean indicating servo is fully counter-clockwise.
        """
        return self._position == 0

    def is_cw(self):
        """Returns Boolean indicating servo is fully clockwise.
        """
        return self._position == +1

    def get_value(self):
        """Returns current position of servo.
        """
        return self._position

    def get_status(self):
        """Gets status of servo.

        :returns: Servo status as string.
        """
        if self.is_ccw():
            return "CLOSED"
        elif self.is_cw():
            return "OPEN"
        else:
            return "ACTIVE"

    
def test_servo():
    pi = pigpio.pi()
    s = GHServo(pi, GHgpio.SERVO_PWM, 1000, 2000)
    print("move to 0")
    s.move(0)
    sleep(3)
    print("move to +1")
    s.move(+1)
    sleep(3)
    print("move to 0")
    s.move(0)
    sleep(3)
    print("move to +1")
    s.move(+1)
    sleep(3)

if __name__ == "__main__":
    test_servo()


