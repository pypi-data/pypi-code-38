# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import CameraSlideForm
from .models import CameraSlide, CameraSlider
from .settings import app_settings


class CameraSliderPlugin(CMSPluginBase):
    name = _('Slider')
    module = _('DjangoCMS Camera Slider')
    model = CameraSlider
    render_template = 'djangocms_cameraslider/_slider.html'
    cache = False
    allow_children = True
    child_classes = ['CameraSlidePlugin']

    def render(self, context, instance, placeholder):
        context = super(CameraSliderPlugin, self).render(context, instance, placeholder)
        context['app_settings'] = app_settings
        return context

plugin_pool.register_plugin(CameraSliderPlugin)


class CameraSlidePlugin(CMSPluginBase):
    name = _('Slide')
    module = _('DjangoCMS Camera Slider')
    model = CameraSlide
    form = CameraSlideForm
    render_template = 'djangocms_cameraslider/_slide.html'
    cache = False
    require_parent = True

plugin_pool.register_plugin(CameraSlidePlugin)
