# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField
from cms.models import CMSPlugin
from filer.fields.image import FilerImageField


@python_2_unicode_compatible
class CameraSlider(CMSPlugin):
    """
    Used to model the image slider.
    """
    name = models.CharField(_('name'), max_length=100)
    slider_id = models.CharField(
        _('slider ID'), max_length=100, default='camera-slider',
        help_text=_('The ID attribute used in the HTML'))
    slider_config = models.TextField(
        _('slider config'), blank=True, null=True,
        help_text=_(
            'The JSON object passed to Camera slider. For more info <a target="'
            '_blank" href="https://www.jqueryscript.net/slideshow/Camera-'
            'Slideshow-Plugin.html">click here</a>')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Camera Slider')
        verbose_name_plural = _('Camera Sliders')


@python_2_unicode_compatible
class CameraSlide(CMSPlugin):
    """
    Used to model the slides in a slider.
    """
    image = FilerImageField()
    caption = HTMLField(
        _('caption'), blank=True, null=True,
        help_text=_('Optional caption that is displayed with the image'))

    def __str__(self):
        if self.caption:
            return self.caption[:50]
        return self.image.url

    class Meta:
        verbose_name = _('Camera Slide')
        verbose_name_plural = _('Camera Slides')
