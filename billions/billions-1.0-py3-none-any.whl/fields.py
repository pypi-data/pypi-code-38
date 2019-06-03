#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import forms
from django.db import models

from .widgets import BillionsMarkdownEditorWidget


class BillionsMarkdownTextField(models.TextField):

    def __init__(self, *args, **kwargs):
        self.config_name = kwargs.pop("config_name", "default")
        super(BillionsMarkdownTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self._get_form_class(),
            'config_name': self.config_name,
        }
        defaults.update(kwargs)
        return super(BillionsMarkdownTextField, self).formfield(**defaults)

    @staticmethod
    def _get_form_class():
        return BillionsMarkdownTextFormField


class BillionsMarkdownTextFormField(forms.fields.CharField):

    def __init__(self, config_name='default', *args, **kwargs):
        kwargs.update({'widget': BillionsMarkdownEditorWidget(config_name=config_name)})
        super(BillionsMarkdownTextFormField, self).__init__(*args, **kwargs)
