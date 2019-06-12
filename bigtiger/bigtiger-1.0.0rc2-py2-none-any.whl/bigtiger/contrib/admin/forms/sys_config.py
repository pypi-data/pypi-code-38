# -*- coding: utf-8 -*-

"""
系统配置
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.sys_config import SysConfigModel


class SysConfigSearchForm(OrderForm):
    config_key = forms.CharField(label='键：', required=False)
    config_name = forms.CharField(label='说明：', required=False)

    def __init__(self, *args, **kwargs):
        super(SysConfigSearchForm, self).__init__(*args, **kwargs)


class SysConfigEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    config_key = forms.CharField(label='键', required=True, max_length=20)
    config_value = forms.CharField(label='值', required=True, )
    config_name = forms.CharField(label='说明', required=True, max_length=200,
                                  widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysConfigEditForm, self).__init__(*args, **kwargs)

    def clean_config_key(self):
        config_key = str(self.cleaned_data['config_key'])
        if config_key != self.cleaned_data['_id']:
            service = SysConfigModel()
            d = service.get_one(config_key)
            if d is not None:
                raise forms.ValidationError('键已存在。')
        return config_key


class SysConfigEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('config_key', 'config_value', 'config_name', ),
                  'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id',), 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysConfigCreateFormAdmin(object):
    pass
