# -*- coding: utf-8 -*-
from PIL import Image
from congo.conf import settings
from urllib.parse import urljoin
from django.utils.safestring import mark_safe
from django.utils.encoding import filepath_to_uri
from django.utils._os import safe_join
import os

class BlankImage(object):
    """
    Klasa reprezentująca puste zdjęcie. Pozwala na skalowanie, zwrot zarówno html jak i odnośnika do pliku.
    """

    def __init__(self):
        self.name = settings.CONGO_BLANK_IMAGE_FILENAME
        self.path = settings.CONGO_BLANK_IMAGE_PATH
        self.url = settings.CONGO_BLANK_IMAGE_URL

    def __str__(self):
        return self.get_path()

    def _get_size(self, max_width, max_height = None):
        if not max_height:
            max_height = max_width

        if not isinstance(max_width, int):
            max_width = settings.CONGO_DEFAULT_IMAGE_WIDTH

        if not isinstance(max_height, int):
            max_height = settings.CONGO_DEFAULT_IMAGE_HEIGHT

        return (max_width, max_height)

    def _resize(self, path, width, height):
        image = Image.open(self.get_path())
        image = image.resize((width, height), Image.ANTIALIAS)
        image.save(path)

        del image

    def render(self, max_width = None, max_height = None, **kwargs):
        url = self.get_url(max_width, max_height)

        width, height = self._get_size(max_width, max_height)
        css_class = kwargs.get('css_class', '')
        alt_text = kwargs.get('alt_text', '')

        html = """<img src="%s" width="%s" height="%s" class="%s" alt="%s" />""" % (url, width, height, css_class, alt_text)
        return mark_safe(html)

    def get_path(self, name = None):
        if not name:
            name = self.name
        return os.path.normpath(safe_join(self.path, name))

    def get_name(self, width, height):
        split = self.name.rsplit('.', 1)
        return '%s_%sx%s.%s' % (split[0], width, height, split[1])

    def get_url(self, max_width = None, max_height = None):
        width, height = self._get_size(max_width, max_height)
        name = self.get_name(width, height)
        path = self.get_path(name)

        if not os.path.isfile(path):
            try:
                self._resize(path, width, height)
            except IOError:
                self.get_path(name)

        return urljoin(self.url, filepath_to_uri(name))
