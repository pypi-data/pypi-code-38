class GHgpio:
    """GPIO definitions for IoT Greenhouse

    This class defines GPIO pins used for 20 pin P1 connector.
    Used during GPIO configuration.
    """
    #_PIN_DEFS__________RPi Pins____________P1 Ribbon Pins___
    RED_LED = 4         #pin 7  GPIO4       P1.1
    WHITE_LED = 14      #pin 8  GPIO14      P1.2
    #GND                #pin 9              P1.3
    BUZZER = 15         #pin 10 GPIO15      P1.4     
    AUX1 = 17           #pin 11 GPIO17      P1.5
    SERVO_PWM = 18      #pin 12 GPIO18      P1.6
    SWITCH_TOGGLE = 27  #pin 13 GPIO27      P1.7
    #GND                #pin 14             P1.8
    FAN = 22            #pin 15 GPIO22      P1.9
    AUX2 = 23           #pin 16 GPIO23      P1.10
    #3.3V               #pin 17             P1.11(PI_PWR_LED) 
    SWITCH_PB = 24      #pin 18 GPIO24      P1.12
    #ANALOG_DIN         #pin 19 SPI0_MIS I  P1.13
    #GND                #pin 20             P1.14
    #ANALOG_D0UT        #pin 21 SPI0_MIS O  P1.15
    TEMP_SENSOR = 25    #pin 22 GPIO25      P1.16
    #ANALOG_CLK         #pin 23 SPIO_S CLK  P1.17
    #ANALOG_CS          #pin 24 SPIO_CE0    P1.18
    #GND                #pin 25             P1.19
    DUAL_LED = 7        #pin 26 GPIO7      P1.20
