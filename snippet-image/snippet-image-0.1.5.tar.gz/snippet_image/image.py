from io import BytesIO
from PIL import (
    Image,
    ImageEnhance,
)

from .size import resize_image_for_snippet
from .text import draw_text_on_image


def create_snippet_image(
        font,
        size=None,
        text='',
        background=None,
        background_color=None,
        overlay=None,
        brightness=None,
        font_color=None,
        font_size=64,
        padding=0.1,
        center=None,
):
    """
    Creates images with a combined cropped background and overlay images and adds text in the center.

    :param font: Path to font file. Is required. For load font used PIL.ImageFont.
    :type font: str
    :param size: Size of snippet image. tuple(width, height).
    :type size: tuple(int, int)
    :param text: Text of snippet image. By default is an empty string.
    :type text: str
    :param background: Path to background image file.
    :type background: str
    :param background_color: Background color of snippet image. Used when background is None.
    :type background_color: tuple(int, int, int)
    :param overlay: Path to overlay image. if size is None, overlay size is used.
                    As an overlay, an image with a transparent background is used.
    :type overlay: str
    :param brightness: Brightness of background of snippet image. Value from 0 to 1.
    :type brightness: float
    :param font_color: Font color in RGBA. By default is (255, 255, 255, 255).
    :type font_color: tuple(int, int, int, int)
    :param font_size: Size of snippet image text. By default is 64.
    :type font_size: int
    :param padding: Text indents to the left and right of the snippet image.
                    Value from 0 to 1.
                    0 - 0% width;
                    1 - 100% width.
    :type padding: float
    :param center : Background image center for crop and resize image. tuple(x, y).
                    Defaults is center of background image.
    :type center: tuple(int, int)

    :return image: BytesIO blob of snippet image,
    :rtype: BytesIO
    """
    background_color = background_color or (0, 0, 0)
    font_color = font_color or (255, 255, 255, 255)

    if not size and not overlay:
        raise TypeError('Overlay and size can not be empty at the same time.')

    overlay_image = overlay and Image.open(overlay)
    size = size or overlay_image.size

    image = get_background_image(
        size,
        background=background,
        background_color=background_color,
        brightness=brightness,
    )

    image = resize_image_for_snippet(image, size, center)

    image = draw_text_on_image(
        image,
        text,
        font,
        font_size,
        font_color,
        padding=padding,
    )

    if overlay_image:
        image.paste(overlay_image, (0, 0), mask=overlay_image)

    image_blob = get_image_blob(image)

    return image_blob


def get_background_image(
        size,
        brightness=None,
        background=None,
        background_color=None,
):
    image_mode = 'RGB'

    if background:
        image = Image.open(background)
    else:
        image = Image.new(image_mode, size, background_color)

    image = image.convert(image_mode) if not image.mode == image_mode else image

    if brightness:
        image = ImageEnhance.Brightness(image).enhance(brightness)

    return image


def get_image_blob(image):
    blob = BytesIO()
    image.save(blob, 'JPEG')

    return blob
