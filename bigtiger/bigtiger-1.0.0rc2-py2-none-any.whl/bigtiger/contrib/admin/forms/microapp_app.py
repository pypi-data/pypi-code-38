# -*- coding: utf-8 -*-

"""
微应用|应用信息
Created on 2017-07-19
@author: linkeddt.com
"""

from __future__ import unicode_literals

from django import forms

from bigtiger.forms.forms import BaseForm, OrderForm
from bigtiger.contrib.admin.models.microapp_app import MicroappAppModel


class MicroappAppSearchForm(OrderForm):
    app_name = forms.CharField(label='App名称：', required=False)

    def __init__(self, *args, **kwargs):
        super(MicroappAppSearchForm, self).__init__(*args, **kwargs)


class MicroappAppEditForm(BaseForm):
    _id = forms.CharField(required=False, widget=forms.HiddenInput)

    id = forms.CharField(label='Id', required=True, max_length=36)
    app_code = forms.CharField(label='App编码', required=True, max_length=10)
    app_name = forms.CharField(label='App名称', required=True, max_length=20)
    app_secret = forms.CharField(label='App安全码', required=True, max_length=36)
    app_summary = forms.CharField(label='App简介', required=False, )
    sso_url = forms.CharField(label='单点登陆URL', required=True, max_length=200,
                              widget=forms.Textarea(attrs={'rows': 2, 'cols': 100}))
    status = forms.ChoiceField(label='状态', required=True)

    def __init__(self, *args, **kwargs):
        super(MicroappAppEditForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = ((1, '启用'), (0, '禁用'),)

    def clean(self):
        cd = super(MicroappAppEditForm, self).clean()

        service = MicroappAppModel()
        m = service.get_one_app_code(cd['app_code'])

        if m is not None and m['id'] != cd['id']:
            self.add_error(
                'app_code', forms.ValidationError('该App编码已存在。'))


class MicroappAppEditFormAdmin(object):
    fieldsets = (
        ('基础信息', {'fields': ('app_code', 'app_name', 'app_secret', 'app_summary',
                             'sso_url', 'status', ), 'classes': ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('_id', 'id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class MicroappAppCreateFormAdmin(object):
    pass
