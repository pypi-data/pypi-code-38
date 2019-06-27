import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import subprocess

from time import sleep
from pibot.nano import Nano


def startup():
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)

    # Initialize library.
    disp.begin()

    # Clear display.
    disp.clear()
    disp.display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Padding
    padding = -2
    top = padding

    # Load default font.
    font = ImageFont.truetype("/home/pi/.fonts/Roboto-Regular.ttf", 16)

    # show TU-Chemnitz logo on screen
    image = Image.open("/home/pi/.resources/tu.pgm").resize((disp.width, disp.height), Image.ANTIALIAS)
    image = image.convert('L')
    image = ImageOps.invert(image)
    image = image.convert('1')
    disp.image(image)
    disp.display()

    sleep(2)
    # show TU-Chemnitz text on screen
    image = Image.open("/home/pi/.resources/tutext.pgm").resize((disp.width, disp.height), Image.ANTIALIAS)
    image = image.convert('L')
    image = ImageOps.invert(image)
    image = image.convert('1')
    disp.image(image)
    disp.display()

    sleep(2)
    # show Roboschool logo on screen
    image = Image.open("/home/pi/.resources/roboschool.pgm").resize((disp.width, disp.height), Image.ANTIALIAS)
    image = image.convert('L')
    image = ImageOps.invert(image)
    image = image.convert('1')
    disp.image(image)
    disp.display()

    # TODO: placeholder for PiBot logo
    # sleep(2)
    # show PiBot logo on screen
    # image = Image.open("/home/pi/.resources/pibot.pgm").resize((disp.width, disp.height), Image.ANTIALIAS)
    # image = image.convert('L')
    # image = ImageOps.invert(image)
    # image = image.convert('1')
    # disp.image(image)
    # disp.display()

    # getting IP
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = (subprocess.check_output(cmd, shell=True)).decode("utf-8")

    # getting voltage
    nano = Nano()
    voltage = nano.get_battery_voltage()

    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, top), "IP: " + str(IP), font=font, fill=255)
    draw.text((0, top + 18), "Battery: {} mV".format(voltage), font=font, fill=255)

    disp.image(image)
    disp.display()
    sleep(2)
