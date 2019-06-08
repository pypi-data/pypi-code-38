# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from django.core.validators import ValidationError

from s3direct.fields import S3DirectField
from aparnik.utils.utils import get_request
from aparnik.settings import aparnik_settings, Setting
from aparnik.utils.utils import document_directory_path
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager

import humanize

request = get_request()


class FileFieldManager(BaseModelManager):

    def get_queryset(self):
        return super(FileFieldManager, self).get_queryset()

    def active(self):
        return super(FileFieldManager, self).active().filter(is_lock=False)


class FileField(BaseModel):
    FILE_MOVIE = 'M'
    FILE_VOICE = 'V'
    FILE_PDF = 'P'
    FILE_IMAGE = 'I'
    FILE_TYPE = (
        (FILE_MOVIE, _('Movie')),
        (FILE_VOICE, _('Voice')),
        (FILE_PDF, _('PDF')),
        (FILE_IMAGE, _('Image')),
    )
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Title'))
    file_s3 = S3DirectField(dest='file', blank=True, null=True, verbose_name=_('File'))
    file_direct = models.FileField(upload_to=document_directory_path, blank=True, null=True, verbose_name=_('File'))
    size = models.IntegerField(default=0, verbose_name=_('File Size'))
    type = models.CharField(max_length=1, null=True, blank=True, choices=FILE_TYPE, verbose_name=_('File Type'))
    is_lock = models.BooleanField(default=False, verbose_name=_('Is lock?'))
    is_encrypt_needed = models.BooleanField(default=False, verbose_name=_('Is encrypt needed?'))
    # این فیلد فقط در کد ها استفاده می شود . در کلین نمی توانیم این کار رو انجام بدیم بدلیل اینکه دو بار فراخوانی می شود.
    is_decrypt_needed = models.BooleanField(default=False, verbose_name=_('Is decrypt needed?'))
    password = models.CharField(max_length=64, default='', blank=True, null=True, verbose_name=_('Password'))
    iv = models.CharField(max_length=64, default='', blank=True, null=True, verbose_name=_('IV'))
    seconds = models.BigIntegerField(default=0, verbose_name=_('Time'))

    objects = FileFieldManager()

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def __unicode__(self):
        return "%s - %s" % (self.id, self.title)

    class Meta:
        verbose_name = _('File Field')
        verbose_name_plural = _('Files Field')
        app_label = 'filefields'

    def clean(self):
        # Don't allow complete action entries.
        if self.id:
            obj = FileField.objects.get(pk=self.id)
        else:
            obj = self

        if self.id and obj.is_lock and self.is_lock:
            raise ValidationError(_('This record locked.'))

        if not self.file_direct and not self.file_s3:
            raise ValidationError(_('File cannot be blank.'))

        if not aparnik_settings.AWS_ACTIVE:

            if not self.id or self.file_direct.path != obj.file_direct.path and self.is_encrypt_needed:
                # encrypt
                self.is_lock = True
            elif not self.is_encrypt_needed and obj.is_encrypt_needed:
                self.is_decrypt_needed = True
                self.is_lock = True
            elif self.is_encrypt_needed and not obj.is_encrypt_needed:
                self.is_lock = True
        # if not self.type:
        #     raise ValidationError({
        #         'type': [_('Value cannot be blank.')],
        #     })

        return super(FileField, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(FileField, self).save(*args, **kwargs)

    def url(self, request=request):
        file = self.file_s3 if aparnik_settings.AWS_ACTIVE else self.file_direct
        # For check value if empty change and check the another one
        if not file:
            file = self.file_s3 if not aparnik_settings.AWS_ACTIVE else self.file_direct

        if hasattr(file, 'url'):
            return request.build_absolute_uri(file.url)

        return file if file else None

    @property
    def file_size(self):
        file = self.file_s3 if aparnik_settings.AWS_ACTIVE else self.file_direct

        if not file:
            file = self.file_s3 if not aparnik_settings.AWS_ACTIVE else self.file_direct

        if hasattr(file, 'size'):
            return file.size

        return self.size

    @property
    def file_size_readable(self):
        return humanize.naturalsize(self.file_size, gnu=True)

    @staticmethod
    def type_icon_url_with_custom_type(type=FILE_IMAGE):
        return Setting.objects.get(key='FILE_TYPE_%s_ICON' % type).get_value()

    @property
    def type_icon_url(self):
        return Setting.objects.get(key='FILE_TYPE_%s_ICON' % self.type).get_value()

    def detect_mime_type(self, mime):

        mime = mime.lower()
        types_map = {
            self.FILE_IMAGE: [
                'image/png',
                'image/jpeg',
                'image/jpg',
            ],
            self.FILE_MOVIE: [
                'video/mpeg',
                'video/mp4',
                'video/x-matroska',
            ],
            self.FILE_PDF: [
                'application/pdf'
            ],
            self.FILE_VOICE: [
                'audio/mpeg',
            ]
        }

        for key in types_map:
            for value in types_map[key]:
                if mime == value:
                    return key
        return None

    def detect_by_readable_description(self, readable_description):

        readable_description = readable_description.lower()

        if readable_description.find('jpeg') != -1 or readable_description.find('png') != -1:

            return self.FILE_IMAGE
        elif readable_description.find('mpeg') != -1:

            return self.FILE_MOVIE
        elif readable_description.find('audio') != -1:

            return self.FILE_VOICE
        elif readable_description.find('pdf') != -1:

            return self.FILE_PDF

        return None