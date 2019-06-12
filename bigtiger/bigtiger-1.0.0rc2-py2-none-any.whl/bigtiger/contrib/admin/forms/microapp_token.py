# -*- coding: utf-8 -*-

"""
微应用|会话票据
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.microapp_token import MicroappTokenModel
from bigtiger.contrib.admin.models.microapp_app import MicroappAppModel


def _get_app_choices():
    service = MicroappAppModel()
    apps = service.get_all()
    if apps:
        return ((item['id'], item['app_name']) for item in apps)
    return None


class MicroappTokenSearchForm(OrderForm):
    app_name = forms.CharField(label='App名称：', required=False)

    def __init__(self, *args, **kwargs):
        super(MicroappTokenSearchForm, self).__init__(*args, **kwargs)


class MicroappTokenEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=True, max_length=36)
    app_id = forms.ChoiceField(label='App名称', required=True)
    app_secret = forms.CharField(label='App安全码', required=True, max_length=36)
    token_code = forms.CharField(label='临时票据', required=True, )
    grant_type = forms.CharField(label='权限类型', required=True, max_length=20)
    session_id = forms.CharField(label='会话Id', required=True, max_length=40)
    expire_date = forms.DateTimeField(label='到期时间', required=True, widget=forms.TextInput(
        attrs={'class': 'form_text from_datetime', 'onClick': 'WdatePicker({dateFmt:"yyyy-MM-dd HH:mm:ss"})'}))

    def __init__(self, *args, **kwargs):
        super(MicroappTokenEditForm, self).__init__(*args, **kwargs)
        self.fields['app_id'].choices = _get_app_choices()


class MicroappTokenEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('app_id', 'app_secret', 'token_code', 'grant_type',
                             'session_id', 'expire_date', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class MicroappTokenCreateFormAdmin(object):
    pass
