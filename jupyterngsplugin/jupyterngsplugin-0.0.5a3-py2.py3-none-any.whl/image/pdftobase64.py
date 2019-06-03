import os

import base64
from wand.image import Image as WImage


def pdftobase64(pdf_file_name, width, height):
    """
    Return base64 image string image from a PDF file to be used in HTML code
    :param pdf_file_name: PDF file name
    :param width: Final image width
    :param height: Final image height
    :return: base64 image string
    """
    if os.path.exists(pdf_file_name):
        with WImage(filename=pdf_file_name) as img:
            img.resize(width, height)
            img = img.convert('png')
            return base64.b64encode(img.make_blob()).decode('utf-8')
    return None
