# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import ModelForm

from .models import CameraSlide


class CameraSlideForm(ModelForm):
    class Meta:
        model = CameraSlide
        fields = '__all__'
