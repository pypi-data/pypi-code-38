from __future__ import unicode_literals

import re

from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ColorInput(forms.TextInput):
    input_type = 'color'


class ColorField(models.CharField):
    default_validators = [RegexValidator(
        re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'),
        _('Enter a valid hex color.'),
        'invalid',
    )]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorInput
        return super(ColorField, self).formfield(**kwargs)
