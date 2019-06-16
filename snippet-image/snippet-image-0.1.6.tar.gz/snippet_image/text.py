from textwrap import wrap
from PIL import (
    ImageDraw,
    ImageFont,
)


def draw_text_on_image(
        image,
        text,
        font,
        font_size,
        font_color,
        padding,
):
    return draw_multiline_text_on_image(
        image,
        text,
        font,
        font_size,
        font_color,
        padding
    ) if text else image


def draw_multiline_text_on_image(
        image,
        text,
        font,
        font_size,
        font_color,
        padding,
):
    """
    Draw text on center image.
    !!! Warning. Image argument is not immutable.
    """
    width, height = image.size

    font = ImageFont.truetype(font, size=font_size, encoding='UTF-8')
    line_length = int((width * (1 - padding)) / (font.getsize(text)[0] / len(text)))
    lines = wrap(text, line_length)

    draw = ImageDraw.Draw(image)

    text_width, text_height = font.getsize_multiline('\n'.join(lines))
    y_text = height / 2 - (text_height / 2)

    for line in lines:
        font_width, font_height = font.getsize(line)
        draw.text(((width - font_width) / 2, y_text), line, font=font, fill=font_color)
        y_text += font_height

    return image
