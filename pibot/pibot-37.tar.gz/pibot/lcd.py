import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps


class LCD:
    def __init__(self, fonttype="/home/pi/.fonts/Roboto-Regular.ttf", fontsize=14):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)

        # Initialize library.
        self.disp.begin()

        self.font = ImageFont.truetype(fonttype, fontsize)

    def print(self, text):
        image = Image.new('1', (self.disp.width, self.disp.height))
        draw = ImageDraw.Draw(image)
        for i in range(len(text)):
            draw.text((0, -2 + i * (self.font.size + 2) ), text[i], font=self.font, fill=255)
        self.disp.image(image)
        self.disp.display()

    def view_image(self, source, invert):
        image = Image.open(source).resize((self.disp.width, self.disp.height), Image.ANTIALIAS)
        if invert:
            image = image.convert('L')
            image = ImageOps.invert(image)
        image = image.convert('1')
        self.disp.image(image)
        self.disp.display()

    def clear(self):
        self.disp.clear()
        self.disp.display()