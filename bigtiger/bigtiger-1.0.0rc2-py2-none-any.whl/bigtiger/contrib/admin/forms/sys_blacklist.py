# -*- coding: utf-8 -*-

"""
Sys_Blacklist
~~~~~~~~~~~~~

系统黑名单
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.sys_blacklist import SysBlacklistModel


class SysBlacklistSearchForm(OrderForm):
    """
    text = forms.CharField(label='文字：', required=False)
    list = forms.ChoiceField(label='下拉框：')
    datetiem = forms.DateField(label='日期：', required=False, widget=forms.TextInput(attrs={'class': 'form-control input-sm','onClick':'WdatePicker()'}))
    """

    def __init__(self, *args, **kwargs):
        super(SysBlacklistSearchForm, self).__init__(*args, **kwargs)


class SysBlacklistEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=False, max_length=36)
    ip = forms.IPAddressField(label='IP', required=True, max_length=50)
    begin_date = forms.DateTimeField(label='开始时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    end_date = forms.DateTimeField(label='截止时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))
    remark = forms.CharField(label='备注', required=False, max_length=200,
                             widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(SysBlacklistEditForm, self).__init__(*args, **kwargs)

    def clean_id(self):
        _id = str(self.cleaned_data['id'])
        if _id != self.cleaned_data['_id']:
            service = SysBlacklistModel()
            d = service.get_one(_id)
            if d is not None:
                raise forms.ValidationError('Id已存在。')
        return _id


class SysBlacklistEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('ip', 'begin_date', 'end_date',
                             'remark', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class SysBlacklistCreateFormAdmin(object):
    pass
