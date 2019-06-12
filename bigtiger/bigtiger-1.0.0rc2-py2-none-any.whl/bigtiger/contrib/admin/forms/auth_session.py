# -*- coding: utf-8 -*-

"""
Auth_Session
~~~~~~~~~~~~~

用户管理|会话信息
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.auth_session import AuthSessionModel


class AuthSessionSearchForm(OrderForm):
    """
    text = forms.CharField(label='文字：', required=False)
    list = forms.ChoiceField(label='下拉框：')
    datetiem = forms.DateField(label='日期：', required=False, widget=forms.TextInput(attrs={'class': 'form-control input-sm','onClick':'WdatePicker()'}))
    """

    def __init__(self, *args, **kwargs):
        super(AuthSessionSearchForm, self).__init__(*args, **kwargs)


class AuthSessionEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    session_key = forms.CharField(label='回话Key', required=True, max_length=40)
    session_data = forms.CharField(label='回话数据', required=True, )
    expire_date = forms.DateTimeField(label='到期时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker()'}))

    def __init__(self, *args, **kwargs):
        super(AuthSessionEditForm, self).__init__(*args, **kwargs)

    def clean_session_key(self):
        session_key = str(self.cleaned_data['session_key'])
        if session_key != self.cleaned_data['_id']:
            service = AuthSessionModel()
            d = service.get_one(session_key)
            if d is not None:
                raise forms.ValidationError('回话Key已存在。')
        return session_key


class AuthSessionEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('session_key', 'session_data',
                             'expire_date', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id',), 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class AuthSessionCreateFormAdmin(object):
    pass
