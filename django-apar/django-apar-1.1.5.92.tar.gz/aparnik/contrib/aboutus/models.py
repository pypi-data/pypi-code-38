# -*- coding: utf-8 -*-


from django.db import models
from aparnik.contrib.users.models import PhoneField
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.socials.models import SocialNetwork
from aparnik.contrib.shortblogs.models import ShortBlog
from aparnik.contrib.filefields.models import FileField
from aparnik.contrib.sliders.models import SliderSegment


# Create your models here.
class InformationManager(models.Manager):
    def get_queryset(self):
        return super(InformationManager, self).get_queryset()

    def get_active(self):
        return self.get_queryset().filter(is_active=True)


class Information(models.Model):
    website = models.URLField(
        max_length=255,
        verbose_name=_('Website')
    )

    address = models.CharField(
        max_length=255,
        verbose_name=_('Address')
    )

    slider_segment_obj = models.ForeignKey(SliderSegment, on_delete=models.CASCADE,
                                           null=True, blank=True, related_name='aboutus_sliders',
                                           verbose_name=_('Slider Segment'))
    phone = PhoneField(
        mobile=False,
        verbose_name=_('Phone Number')
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email')
    )

    about_us = models.TextField(
        verbose_name=_('About Us'),
    )

    image = models.ForeignKey(FileField, on_delete=models.CASCADE, verbose_name=_('Image'))

    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True
    )
    socials = models.ManyToManyField(SocialNetwork, verbose_name=_('Socials'))
    short_blogs = models.ManyToManyField(ShortBlog, verbose_name=_('Content Segment'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = InformationManager()

    def save(self, *args, **kwargs):

        return super(Information, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Information, self).__init__(*args, **kwargs)

    class Meta:
        # ordering = ['latitude', 'longitude']
        verbose_name = _('Information')
        verbose_name_plural = _('Informations')
