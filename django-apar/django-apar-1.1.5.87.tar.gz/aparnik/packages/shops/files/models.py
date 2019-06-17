# -*- coding: utf-8 -*-


from django.db import models
from polymorphic.models import PolymorphicManager, PolymorphicModel
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode, b64decode

from aparnik.contrib.filefields.models import FileField
from aparnik.packages.shops.products.models import Product, ProductManager


# Base FIle MANAGER
class FileManager(ProductManager):

    def get_queryset(self):
        return super(FileManager, self).get_queryset()

    def active(self, user=None):
        return super(FileManager, self).active(user).filter(file_obj__is_lock=False, publish_date__lte=now())

    def get_this_user(self, user):
        # TODO: add handler for user
        return self.get_queryset().all()

    def get_this_type(self, type):
        return self.active().filter(file_obj__type=type)


# Base File class
class File(Product):
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    file_obj = models.ForeignKey(FileField, related_name='shop_file_obj', on_delete=models.CASCADE, verbose_name=_('File'))
    banner = models.ForeignKey(FileField, related_name='shop_file_banner', null=True, blank=True,
                               on_delete=models.CASCADE, verbose_name=_('Banner Image'))
    cover = models.ForeignKey(FileField,  null=True, blank=True, related_name='shop_file_cover', on_delete=models.CASCADE, verbose_name=_('Cover Image'))
    publish_date = models.DateTimeField(default=now, verbose_name=_('Publish Date'))

    objects = FileManager()

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('File')
        verbose_name_plural = _('Files')

    def get_api_file_download_request_uri(self):
        return reverse('aparnik-api:shops:files:download-request', args=[self.id])

    def get_key_url(self, user, key):
        if not self.has_permit(user=user):
            raise ValidationError({'__all__': [_('You must buy this File.')]})
        try:
            if self.file_obj.password:
                ciphertext = ''
                if key == 'AAAAaaaa.':
                    ciphertext = self.file_obj.password.encode()
                else:
                    public_key = RSA.importKey(b64decode(key))
                    cipher = PKCS1_v1_5.new(public_key)
                    ciphertext = cipher.encrypt(self.file_obj.password.encode())
                password = b64encode(ciphertext)
            else:
                password = None
            return password, self.file_obj.iv, self.file_obj.url()
        except Exception as e:
            raise ValidationError({'__all__': [_('Wrong key or fail on encryption.')]})

    def get_api_progress_set_uri(self):
        return reverse('aparnik-api:educations:progresses:set', args=[self.id])
