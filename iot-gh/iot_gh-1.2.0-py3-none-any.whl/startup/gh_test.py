from time import sleep
from iot_gh.IoTGreenhouse import IoTGreenhouse
from iot_gh.IoTGreenhouseService import IoTGreenhouseService


ghs = None      #iot_greenhouse_service
gh = None       #iot_greenhouse data object

def lamp_test():
    global ghs 
    print("Testing lamps...")
    print("Light red")
    ghs.lamps.red.on() 
    sleep(2)
    ghs.lamps.red.off() 
    sleep(1)
    print("Light white")
    ghs.lamps.white.on() 
    sleep(2)
    ghs.lamps.white.off() 
    sleep(1)
    print("Light green")
    ghs.lamps.dual.on_green() 
    sleep(2)
    ghs.lamps.dual.off() 
    sleep(1)
    print("Light yellow")
    ghs.lamps.dual.on_yellow() 
    sleep(2)
    ghs.lamps.dual.off() 
    sleep(1)
    print("Lamp test done.")
    print()

def switch_test():
    global ghs 

    print("Testing switches. PB activates Red LED, Toggle activates White LED.")
    print("Switch both to on to end.")
    while(ghs.switches.push_button.get_state() == ghs.switches.SWITCH_OFF or 
          ghs.switches.toggle.get_state() == ghs.switches.SWITCH_OFF):
        
        if ghs.switches.push_button.get_state() == ghs.switches.SWITCH_ON:
            ghs.lamps.red.on()
        else:
            ghs.lamps.red.off() 
        if ghs.switches.toggle.get_state() == ghs.switches.SWITCH_ON:
            ghs.lamps.white.on()
        else:
            ghs.lamps.white.off()
    
    ghs.lamps.red.off()
    ghs.lamps.white.off()        
    print("Switch test done.")
    print()

def fan_test():
    global ghs
    
    print("Testing fan.")
    
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_ON):
        print("Toggle must be off for test to start.")
        sleep(1)
    print("Press push botton to activitate fan. Turn toggle on to end.")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_OFF):
        if ghs.switches.push_button.get_state() == ghs.switches.SWITCH_ON:
            ghs.fan.on()
        else:
            ghs.fan.off()
    ghs.fan.off()        
    print("Fan test done.")
    print()

def servo_test():
    global ghs 

    print("Testing servo.")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_ON):
        print("Toggle must be off for test to start.")
        sleep(1)
    print("Servo moves between min and max Turn toggle on to end.")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_OFF):
        pos = 0
        while pos > -1:
            ghs.servo.move(pos)
            pos -= .1
            sleep(.2)
        pos = -1
        while pos < 1:
            ghs.servo.move(pos)
            pos += .1
            sleep(.2)
        pos = 1
    print("Servo test done.")
    print()

def temp_sensor_test():
    global ghs 
    print("Testing temp sensor.")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_ON):
        print("Toggle must be off for test to start.")
        sleep(1)
    print("Turn toggle on to end.")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_OFF):
            print("i temp C: %d" % ghs.temperature.get_inside_temp_C())
            print("i temp F: %d" % ghs.temperature.get_inside_temp_F())
            print("o temp C: %d" % ghs.temperature.get_outside_temp_C())
            print("o temp F: %d" % ghs.temperature.get_outside_temp_F())
            print()
            sleep(1)
    print("Temp sensor test done.")
    print()    

def analog_test():

    print("Testing analog inputs")
    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_ON):
        pass #wait for toggle off

    while(ghs.switches.toggle.get_state() == ghs.switches.SWITCH_OFF):
 
        print("Pot value: %i" % ghs.analog.pot.get_value())
        print("Light value:" + str(ghs.analog.light.get_value()))
        print("Aux value:" + str(ghs.analog.aux.get_value()))
        print()
        sleep(1)

def test_all():
    global ghs
    
    print("GH test - testing all.")   
    ghs = IoTGreenhouseService()
    iot_greenhouse = ghs.make_greenhouse("test")
    
    ghs.buzzer.beeps(beepcount = 1)
    lamp_test()
    ghs.buzzer.beeps(beepcount = 2)
    switch_test()
    ghs.buzzer.beeps(beepcount = 3)
    fan_test()
    ghs.buzzer.beeps(beepcount = 4)
    servo_test()
    ghs.buzzer.beeps(beepcount = 5)
    temp_sensor_test()
    ghs.buzzer.beeps(beepcount = 6)
    analog_test()
   
    print("GH test completed.")   

if __name__ == "__main__":
    test_all()



