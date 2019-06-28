import datetime
import pigpio
import configparser, os

from iot_gh.GHgpio import GHgpio
from iot_gh.GHAnalogService import GHAnalogService
from iot_gh.GHBuzzer import GHBuzzer
from iot_gh.GHFan import GHFan
from iot_gh.GHLamps import GHLamps
from iot_gh.GHServo import GHServo
from iot_gh.GHSwitches import GHSwitches
from iot_gh.GHTemperature import GHTemperature
from iot_gh.GHWebService import GHWebService
from iot_gh.IoTGreenhouse import IoTGreenhouse

class GHService(object):
    """A container class for IoT Greenhouse services.
    
    Provides references to component services. Component factory.
    """
      
    def __init__(self, pi, spi):
        """Initializes an IoT Greenhouse container.
        """
        self._pi = pi
        self._spi = spi

        if not self._pi.connected:
            print("ERROR: unable to connect to pigpio")
            exit()
        self._read_config()
        self._make_components()
        self.greenhouse = self._make_greenhouse("new greenhouse")
        self.update_greenhouse()

    def _read_config(self):
        """Loads configuration file from user iot_gh directory.
        """
        try:
            config = configparser.ConfigParser()
            
            if type(self._pi) is not pigpio.pi: #debug mode. Load test file
               config.read("./iot_gh_system.conf")
            else:
                config.read(["iot_gh_system.conf", os.path.expanduser("~/.iot_gh/iot_gh_system.conf")],encoding="UTF8")
            self.version = config["IOT_GREENHOUSE"]["VERSION"]
            self._url = config["IOT_GREENHOUSE"]["URL"]
            self._servo_ccw_limit = int(config["IOT_GREENHOUSE"]["SERVO_CCW_LIMIT"])
            self._servo_cw_limit = int(config["IOT_GREENHOUSE"]["SERVO_CW_LIMIT"])
        except Exception as ex:
            raise Exception("Unable to load IoT Greenhouse System Configuration. %s" % ex.args[0])
       
    def _make_components(self):
        """Makes component services for IoT Greenhouse container.
        """
        self.analog = GHAnalogService(self._pi, self._spi)
        self.buzzer = GHBuzzer(self._pi, GHgpio.BUZZER)
        self.fan = GHFan(self._pi, GHgpio.FAN)
        self.lamps = GHLamps(self._pi, GHgpio.RED_LED, GHgpio.WHITE_LED, GHgpio.RED_LED, GHgpio.DUAL_LED)
        self.servo = GHServo(self._pi, GHgpio.SERVO_PWM, self._servo_cw_limit, self._servo_ccw_limit)
        self.switches = GHSwitches(self._pi, GHgpio.SWITCH_PB, GHgpio.SWITCH_TOGGLE)
        self.temperature = GHTemperature(self.analog.aux, self.analog.temp)
        self.web_service = GHWebService(self)    
        
    def _make_greenhouse(self, name):
        """Factory class to build IoT Greenhouse data object.
        """
        gh = IoTGreenhouse()
        gh.name = name
        
        #read greenhouse config values
        config = configparser.ConfigParser()
        if type(self._pi) is not pigpio.pi: #debug mode. Load test file
            config.read("./iot_gh.conf")
        else:
            config.read(["iot_gh.conf", os.path.expanduser("~/.iot_gh/iot_gh.conf")],encoding="UTF8")
        gh.house_id = config["IOT_GREENHOUSE"]["HOUSE_ID"]
        gh.group_id = config["IOT_GREENHOUSE"]["GROUP_ID"]
        gh.house_number = config["IOT_GREENHOUSE"]["HOUSE_NUMBER"].zfill(2)
        gh.version = self.version

        return gh
    
    def update_greenhouse(self):
        """Updates IoTGreenhouse object by reading all house 
        states and refreshing gh object.
        """
        try:
    
            self.greenhouse.led_red_state = self.lamps.red.get_state()
            self.greenhouse.led_red_status = self.lamps.red.get_status()
            self.greenhouse.led_white_state = self.lamps.white.get_state()
            self.greenhouse.led_white_status = self.lamps.white.get_status()
            self.greenhouse.led_dual_state =  self.lamps.dual.get_state()
            self.greenhouse.led_dual_status = self.lamps.dual.get_status()
            self.greenhouse.switch_pb_state = self.switches.push_button.get_state()
            self.greenhouse.switch_pb_status = self.switches.push_button.get_status()
            self.greenhouse.switch_toggle_state = self.switches.toggle.get_state()
            self.greenhouse.switch_toggle_status = self.switches.toggle.get_status()
            self.greenhouse.fan_state =  self.fan.get_state()
            self.greenhouse.fan_status =  self.fan.get_status()
            self.greenhouse.servo_position = self.servo.get_value()
            self.greenhouse.servo_status = self.servo.get_status()
            self.greenhouse.heater_state = self.lamps.white.get_state()
            self.greenhouse.heater_status = self.lamps.white.get_status()
            self.greenhouse.buzzer_state = self.buzzer.get_state()
            self.greenhouse.buzzer_status = self.buzzer.get_status()
            self.greenhouse.ain_pot_raw = self.analog.pot.get_value()
            self.greenhouse.ain_light_raw =  self.analog.light.get_value()
            self.greenhouse.ain_aux_raw =  self.analog.aux.get_value()

            self.greenhouse.temp_inside_C = self.temperature.get_inside_temp_C()
            self.greenhouse.temp_inside_F = self.temperature.get_inside_temp_F()
            self.greenhouse.temp_outside_C = self.temperature.get_outside_temp_C()
            self.greenhouse.temp_outside_F = self.temperature.get_outside_temp_F()
            
            self.greenhouse.last_update = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
            
            self._make_message()
            

        except Exception as e:
            self.greenhouse.message = "Updata exception: %s" % e.args[0]
            
    def _make_message(self):
        m = ""
        gh = self.greenhouse
        if  gh.temp_outside_C > gh.temp_inside_C: 
            m = "Warning: The temperature outside the greenhouse is higher than the internal temperature."
        elif gh.servo_status == "CLOSED" and gh.fan_status == "ON":
            m = "Error: The fan is activated by louvers are closed."
        else:
            m = "Greenhouse status is normal."

        gh.message = m