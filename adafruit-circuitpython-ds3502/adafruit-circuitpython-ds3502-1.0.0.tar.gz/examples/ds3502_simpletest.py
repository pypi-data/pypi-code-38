from time import sleep
import board
import adafruit_ds3502
from analogio import AnalogIn

i2c = board.I2C()
ds3502 = adafruit_ds3502.DS3502(i2c)
wiper_output = AnalogIn(board.A0)

ds3502.wiper = 127
print("Wiper value: %d"%wiper_output.value)
sleep(1.0)

ds3502.wiper = 0
print("Wiper value: %d"%wiper_output.value)
