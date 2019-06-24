# -*- coding:utf-8 -*-
__author__ = 'denishuang'
from qrcode.image import pil
from qrcode import QRCode
from PIL import Image, ImageDraw
from django.db.models.fields.files import ImageFieldFile


class PilImage(pil.PilImage):
    def __init__(self, border, width, box_size, *args, **kwargs):
        self.front_color = kwargs.get("front_color", "black")
        self.background_color = kwargs.get("background_color", "white")
        super(PilImage, self).__init__(border, width, box_size, *args, **kwargs)

    def new_image(self, **kwargs):
        img = Image.new("RGBA", (self.pixel_size, self.pixel_size), self.background_color)
        self._idr = ImageDraw.Draw(img)
        return img

    def drawrect(self, row, col):
        box = self.pixel_box(row, col)
        self._idr.rectangle(box, fill=self.front_color)


def make_qrcode(url, logo=None, **kwargs):
    if isinstance(logo, ImageFieldFile) and logo:
        logo = Image.open(logo)
    code = QRCode()
    code.add_data(url)
    img = code.make_image(PilImage, **kwargs)
    if logo:
        logo_size = kwargs.get("logo_size", 60)
        pos = (img.size[0] - logo_size) / 2
        img._img.paste(logo.resize((logo_size, logo_size)), (pos, pos))
        logo.seek(0)
    return img


def make_qrcode_response(url, logo=None, **kwargs):
    import cStringIO
    from django.http.response import StreamingHttpResponse
    fileIO = cStringIO.StringIO()
    code = make_qrcode(url, logo, **kwargs)
    code.save(fileIO)
    fileIO.seek(0)
    return StreamingHttpResponse(fileIO, content_type="image/png")


def qrcode(request):
    return make_qrcode_response(request.GET['url'])
