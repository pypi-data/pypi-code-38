# -*- coding: utf-8 -*-
from django.db import models
from congo.gallery.models import get_watermark_choice

class MediaMixin(models.Model):
    watermark = models.CharField("Znak wodny", max_length = 50, null = True, blank = True, choices = get_watermark_choice())
    hide_photos = models.BooleanField("Nie pokazuj zdjęć", default = False, help_text = "Blokuj automatyczne wyświetlanie galerii zdjęć pod treścią")
    hide_videos = models.BooleanField("Nie pokazuj filmów", default = False, help_text = "Blokuj automatyczne wyświetlanie filmów pod treścią")

    class Meta:
        abstract = True

#    @property
#    def photo(self):
#        if not hasattr(self, '_photo'):
#            from gallery.models import ContentPhoto
#            self._photo = ContentPhoto.get_photo_for_object(self)
#        return self._photo
#
#    @photo.setter
#    def photo(self, _photo):
#        self._photo = _photo
#
#    def get_photos(self):
#        if not hasattr(self, '_photos'):
#            from gallery.models import ContentPhoto
#            self._photos = ContentPhoto.get_photos_for_object(self)
#        return self._photos
#
#    def get_videos(self):
#        if not hasattr(self, '_videos'):
#            from gallery.models import ContentVideo
#            self._videos = ContentVideo.get_videos_for_object(self)
#        return self._videos
