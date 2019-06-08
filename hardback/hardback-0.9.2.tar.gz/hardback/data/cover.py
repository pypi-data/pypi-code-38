from attr import dataclass, Factory
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont

# TODO: this only works for MacOS
DEFAULT_FONT = '/Library/Fonts/Arial.ttf'


@dataclass
class Font:
    name: str = ''
    size: int = 0

    def create(self):
        name = self.name or DEFAULT_FONT
        suffix = Path(name).suffix
        if suffix == '.ttf':
            if not self.size:
                raise ValueError(f'Size must be set for Truetype fonts')
            return ImageFont.truetype(name, self.size)

        if suffix == '.pil':
            if self.size:
                raise ValueError(f'Size cannot be set for Bitmap fonts')
            return ImageFont.load(name)

        raise ValueError(f'Do not understand font {name}')


@dataclass
class Cover:
    title: str = ''
    image: str = ''
    font: Font = Factory(Font)
    margin: List[int] = Factory(lambda: [75, 50])
    size: List[int] = Factory(lambda: [1600, 2560])

    def render(self):
        image = Image.new('RGB', self.size, 'white')
        draw = ImageDraw.Draw(image)
        items = []

        if self.title:
            font = self.font.create()
            width, height = font.getsize(self.title)
            x = (self.size[0] - width) // 2

            def run(y):
                draw.text((x, y), text=self.title, font=font, fill='black')

            items.append((run, height))

        if self.image:
            cimage = Image.open(self.image)
            ratio = (self.size[0] - 2 * self.margin[0]) / cimage.size[0]
            new_size = [round(ratio * i) for i in cimage.size]
            cimage = cimage.resize(new_size, Image.BOX)

            def run(y):
                image.paste(cimage, (self.margin[0], y))

            items.append((run, new_size[1]))

        if items:
            remains = self.size[1] - sum(height for run, height in items)
            spacing = int(remains / (len(items) + 1))
            y = spacing
            for run, height in items:
                run(y)
                y += height + spacing

        return image


# See https://blog.reedsy.com/book-cover-dimensions/
