import pigpio
from iot_gh.GHgpio import GHgpio
from iot_gh.GHFan import GHFan
from iot_gh.GHSwitches import GHSwitches
from iot_gh.startup.gh_test import test_all

def startup():
    ''' Startup code called during IoT Greenhouse startup

    Turns off fan (currently active high and pull-up enables. Change in future versions)
    Tests pb switch. If depressed during startup, run board test.
    '''
    pi = pigpio.pi()

    fan = GHFan(pi, GHgpio.FAN)
    fan.off()

    switches = GHSwitches(pi, GHgpio.SWITCH_PB, GHgpio.SWITCH_TOGGLE)
    if switches.push_button.get_state() == GHSwitches.SWITCH_ON:
        print("testing")
        test_all()



if __name__ == "__main__":
    startup()
