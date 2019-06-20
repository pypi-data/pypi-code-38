# -*- coding: utf-8 -*-
from PIL import Image
from congo.utils.classes import BlankImage
from congo.utils.text import slugify
from django.conf import settings
from django.db.models import ImageField, signals
from django.db.models.fields.files import ImageFieldFile
from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri
from django.utils.safestring import mark_safe
from unidecode import unidecode
import math
import os
import re
import urlparse

class MultisizeImageFieldFile(ImageFieldFile):
    FIT = 1
    FILL = 2
    CROP = 3

    def save(self, name, content, save = True):
        name = unidecode(name).lower()
        if "." in name:
            base, ext = name.rsplit('.', 1)
            base = slugify(base)
            name = '%s-original.%s' % (base, ext)
        else:
            name = '%s-original' % slugify(name)
        super(MultisizeImageFieldFile, self).save(name, content, save)

    def delete(self, save = True):
        self._delete_resized()

        super(MultisizeImageFieldFile, self).delete(save)

    def _get_mode(self, crop = False, fill = False):
        if crop:
            return self.CROP
        elif fill:
            return self.FILL
        return self.FIT

    def _get_size(self, max_width, max_height = None, mode = FIT):
        try:
            if not isinstance(max_width, int):
                max_width = settings.CONGO_DEFAULT_IMAGE_WIDTH

            if not isinstance(max_height, int):
                max_height = settings.CONGO_DEFAULT_IMAGE_HEIGHT

            if mode == self.FILL:

                if self.width > max_width and self.height > max_height:
                    scale = self.width / float(max_width)
                    width = max_width
                    height = int(self.height / scale)

                    if height < max_height:
                        scale = self.height / float(max_height)
                        height = max_height
                        width = int(self.width / scale)
                elif self.width > max_width:
                    scale = self.width / float(max_width)
                    width = max_width
                    height = int(self.height / scale)
                elif self.height > max_height:
                    scale = self.height / float(max_height)
                    height = max_height
                    width = int(self.width / scale)
                else:
                    width = self.width
                    height = self.height

            elif mode == self.CROP:

                if self.width > max_width:
                    width = max_width
                else:
                    width = self.width

                if self.height > max_height:
                    height = max_height
                else:
                    height = self.height

            elif mode == self.FIT:

                if self.width > max_width or self.height > max_height:
                    self_scale = 1. * self.width / self.height
                    max_scale = 1. * max_width / max_height

                    if max_scale < self_scale:
                        if self.width > max_width:
                            scale = 1. * self.width / max_width
                            width = max_width
                            height = int(self.height / scale)
                        else:
                            width = self.width
                            height = self.height

                        if height > max_height:
                            scale = 1. * height / max_height
                            height = max_height
                            width = int(width / scale)
                    else:
                        if self.height > max_height:
                            scale = 1. * self.height / max_height
                            height = max_height
                            width = int(self.width / scale)

                        else:
                            width = self.width
                            height = self.height

                        if width > max_width:
                            scale = 1. * width / max_width
                            width = max_width
                            height = int(height / scale)
                else:
                    width = self.width
                    height = self.height

            return (width, height)
        except IOError:
            return (max_width, max_height)

    def _paste_watermark(self, image, width, height):

        if width > settings.CONGO_WATERMARK_MIN_WIDTH and height > settings.CONGO_WATERMARK_MIN_HEIGHT:
            if hasattr(self, 'watermark') and self.watermark:
                watermark = Image.open(os.path.join(settings.CONGO_WATERMARK_PATH, self.watermark))
                resize = False

                if watermark.size[0] + 20 > width:
                    watermark_width = width - 20
                    watermark_height = int(watermark.size[1] * watermark_width / float(watermark.size[0]))
                    resize = True
                else:
                    watermark_width = watermark.size[0]
                    watermark_height = watermark.size[1]

                if watermark.size[1] + 20 > height:
                    watermark_height = height - 20
                    watermark_width = int(watermark.size[0] * watermark_height / float(watermark.size[1]))
                    resize = True

                if resize:
                    watermark = watermark.resize((watermark_width, watermark_height), Image.ANTIALIAS)

                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                layer = Image.new('RGBA', image.size, (0, 0, 0, 0))

                horizontal = settings.CONGO_WATERMARK_HORIZONTAL_POSITION
                vertical = settings.CONGO_WATERMARK_VERTICAL_POSITION

                if horizontal == 'L':
                    position_x = 20
                elif horizontal == 'R':
                    position_x = width - watermark_width - 20
                else:
                    position_x = int((width - watermark_width) / 2)

                if vertical == 'T':
                    position_y = 20
                elif vertical == 'B':
                    position_y = height - watermark_height - 20
                else:
                    position_y = int((height - watermark_height) / 2)

                position = (position_x, position_y)
                layer.paste(watermark, position)

                image = Image.composite(layer, image, layer)
                image = image.convert('RGB')
        return image

    def _resize(self, path, width, height, mode = FIT):
        image = Image.open(self.path)

        if path.endswith(".gif"):
            self.gif_resize(self.path, image, width, height)
            return
        elif mode == self.CROP:
            _width, _height = self._get_size(width, height, self.FILL)
            image = image.resize((_width, _height), Image.ANTIALIAS)
            x = int(math.ceil((_width - width) / 2))
            y = int(math.ceil((_height - height) / 2))

            # sprawdzamy, czy moze spowodowac blad, w teorii tak, a w praktyce?
            image = image.crop((x, y, x + width, y + height))
        else:
            image = image.resize((width, height), Image.ANTIALIAS)

        image = self._paste_watermark(image, width, height)
        image.save(path)
        del image

    def _delete_resized(self):
        path, name = os.path.split(self.get_path(self.name))
        pattern = name[::-1].replace("original"[::-1], "(\d+)x(\d+)"[::-1], 1)[::-1]

        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) and re.match(pattern, filename):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

    def get_name(self, width, height):
        return self.name[::-1].replace("original"[::-1], ("%sx%s" % (width, height))[::-1], 1)[::-1]

    def get_path(self, name):
        return os.path.normpath(safe_join(settings.MEDIA_ROOT, name))

    def get_url(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        width, height = self._get_size(max_width, max_height, mode)
        name = self.get_name(width, height)
        path = self.get_path(name)

        if not os.path.isfile(path):
            try:
                self._resize(path, width, height, mode)
            except IOError:
                return BlankImage().get_url(max_width, max_height)

        return urlparse.urljoin(settings.MEDIA_URL, filepath_to_uri(name))

    def get_width(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        return self._get_size(max_width, max_height, mode)[0]

    def get_height(self, max_width = None, max_height = None, crop = False):
        mode = self._get_mode(crop)
        return self._get_size(max_width, max_height, mode)[1]

    def render(self, max_width = None, max_height = None, crop = False, **kwargs):
        url = self.get_url(max_width, max_height, crop)

        css_class = kwargs.get('css_class', '')
        alt_text = kwargs.get('alt_text', '')
        title = kwargs.get('title', '')

        html = """<img src="%s" class="%s" alt="%s" title="%s" />""" % (url, css_class, alt_text, title)
        return mark_safe(html)

# Obsluga gifow
    def gif_resize(self, path, image, width, height):
        from PIL import ImageSequence

        # Output (max) size
        size = width, height

        frames = ImageSequence.Iterator(image)

        # Wrap on-the-fly thumbnail generator
        def thumbnails(frames):
            for frame in frames:
                thumbnail = frame.copy()
                thumbnail.thumbnail(size, Image.ANTIALIAS)
                yield thumbnail

        frames = thumbnails(frames)

        # Save output
        om = next(frames) # Handle first frame separately
        om.info = image.info # Copy sequence info
        om.save(path.replace('original', (u'%sx%s' % (width, height))), save_all = True, append_images = list(frames))

class MultisizeImageField(ImageField):
    attr_class = MultisizeImageFieldFile

    def __init__(self, verbose_name = None, name = None, watermark_field = None, **kwargs):
        self.watermark_field = watermark_field
        super(MultisizeImageField, self).__init__(verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        super(MultisizeImageField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.update_watermark, sender = cls)

    def update_watermark(self, instance, *args, **kwargs):
        image_file = getattr(instance, self.attname)

        if not image_file:
            return

        if self.watermark_field:
            image_file.watermark = getattr(instance, self.watermark_field)
