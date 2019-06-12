# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals

import os
import json

from django import forms
from django.forms.forms import BoundField

from bigtiger.forms.widgets import UploadFile

__all__ = (
    'BaseForm', 'ExcelImportForm', 'ExcelImportFormAdmin',
)


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('r', None)
        self.context = kwargs.get('c', None)

        if self.request is not None:
            del kwargs['r']
        if self.context is not None:
            del kwargs['c']
        super(BaseForm, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key %r not found in '%s'" % (name, self.__class__.__name__))

        widget = field.widget
        if not isinstance(widget, forms.CheckboxInput):
            attrs = widget.attrs
            if 'class' not in attrs:
                attrs.update({'class': 'form-control input-sm'})
        return BoundField(self, field, name)


class OrderForm(BaseForm):
    sort = forms.CharField(label='sort', required=False)
    order = forms.CharField(label='order', required=False)


class ExcelImportForm(BaseForm):
    excel_file = forms.CharField(label='Excel文件', max_length=200, required=True,
                                 widget=UploadFile(attrs={'accept': '.xls,.xlsx'}))

    def clean_excel_file(self):
        value = self.cleaned_data['excel_file']
        d = json.loads(value)
        file_name = d['filename']
        flag = d['flag']
        if flag == 'add':
            extension = os.path.splitext(file_name)[1][1:]
            if extension not in ('xls', 'xlsx',):
                raise forms.ValidationError('文件格式不正确，请上传excel文件。')
            return value
        else:
            return file_name


class ExcelImportFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('excel_file', ),
                  'classes': ('col-sm-12', 'form-vertical',)}),
        ('隐藏域', {'fields': (), 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()
