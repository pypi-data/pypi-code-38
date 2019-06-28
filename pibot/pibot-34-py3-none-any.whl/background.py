import RPi.GPIO as GPIO
from os import popen
from time import sleep

# display stuff
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

POWER_OFF_PIN = 21


def background():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_OFF_PIN, GPIO.IN, GPIO.PUD_UP)

    # 128x64 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
    # Initialize library.
    disp.begin()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    font = ImageFont.truetype("/home/pi/.fonts/Roboto-Regular.ttf", 16)

    while 1:
        if not GPIO.input(POWER_OFF_PIN):
            time_till_shutoff = 5
            while not GPIO.input(POWER_OFF_PIN):  # Draw a black filled box to clear the image.
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                draw.text((x, top), "Poweroff in: " + str(time_till_shutoff), font=font, fill=255)
                # Display image.
                disp.image(image)
                disp.display()
                time_till_shutoff = time_till_shutoff - 1
                sleep(1)
                if time_till_shutoff <= 0:
                    # Draw a black filled box to clear the image.
                    draw.rectangle((0, 0, width, height), outline=0, fill=0)
                    draw.text((x, top), "Powering off...", font=font, fill=255)
                    disp.image(image)
                    disp.display()
                    sleep(1)
                    popen("sudo poweroff")
                    break
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            disp.image(image)
            disp.display()
        sleep(0.5)
