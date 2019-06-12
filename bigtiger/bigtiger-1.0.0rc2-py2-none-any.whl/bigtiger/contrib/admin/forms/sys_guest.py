# -*- coding: utf-8 -*-

"""
Sys_Guest
~~~~~~~~~~~~~

系统访客
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.widgets import QuickDateSelectorField
from bigtiger.contrib.admin.models.sys_guest import SysGuestModel


class SysGuestSearchForm(OrderForm):
    daterange = QuickDateSelectorField(label='访问时间', required=False)
    location = forms.CharField(label='地理位置', required=False)

    def __init__(self, *args, **kwargs):
        super(SysGuestSearchForm, self).__init__(*args, **kwargs)


class SysGuestEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=False, max_length=36)
    ip = forms.CharField(label='访客IP', required=True, max_length=50)
    request_date = forms.DateTimeField(label='访问时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    location = forms.CharField(label='地理位置', required=False, max_length=200,
                               widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysGuestEditForm, self).__init__(*args, **kwargs)

    def clean_id(self):
        _id = str(self.cleaned_data['id'])
        if _id != self.cleaned_data['_id']:
            service = SysGuestModel()
            d = service.get_one(_id)
            if d is not None:
                raise forms.ValidationError('Id已存在。')
        return _id


class SysGuestEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('ip', 'request_date', 'location',
                             'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysGuestCreateFormAdmin(object):
    pass
