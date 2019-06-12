# -*- coding: utf-8 -*-

'''
Created on 2014-5-18
@author: linkeddt.com
'''

from __future__ import unicode_literals

import json

from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel
from bigtiger.core.exceptions import AuthenticateError, SuspiciousOperation
from bigtiger.forms.forms import BaseForm
from bigtiger.views.generic import (SysConfContextMixin, TemplateResponseMixin,
                                    UpdateView, View)
from django import forms
from django.conf import settings
from django.contrib import auth
from django.shortcuts import HttpResponseRedirect
from django.utils.module_loading import import_string
from django_restful import RestfulApiError
from django_sae.models.user import UserModel


def load_backend(path):
    return import_string(path)()


class LoginForm(forms.Form):
    username_error = {'required': '请输入用户名'}
    password_error = {'required': '请输入密码'}
    username = forms.CharField(label='用户名：', max_length=30,  widget=forms.TextInput(
        attrs={'class': 'form-control input-lg', 'placeholder': '请输入用户名'}), error_messages=username_error)
    password = forms.CharField(label='密码：',  max_length=30, widget=forms.PasswordInput(
        attrs={'class': 'form-control input-lg', 'placeholder': '请输入密码'}), error_messages=password_error)


class PwdModifyForm(BaseForm):
    user_id = forms.CharField(widget=forms.HiddenInput)
    old_pwd = forms.CharField(
        label='旧的密码', max_length=30, widget=forms.PasswordInput)
    new_pwd = forms.CharField(
        label='新的密码', max_length=30, widget=forms.PasswordInput)
    confirm_pwd = forms.CharField(
        label='确认密码', max_length=30, widget=forms.PasswordInput)

    def clean_confirm_pwd(self):
        new_pwd = self.cleaned_data['new_pwd']
        confirm_pwd = self.cleaned_data['confirm_pwd']
        if new_pwd == confirm_pwd:
            return confirm_pwd
        raise forms.ValidationError('确认密码与新密码不一致。')


class PwdModifyFormAdmin(object):
    fieldsets = (
        ('修改密码', {'fields': ('old_pwd', 'new_pwd', 'confirm_pwd',),
                  'classes':  ('col-sm-12', 'form-horizontal',)}),
        ('隐藏域', {'fields': ('user_id',),
                 'classes': ('col-sm-12', 'hidefield',)}),
    )
    readonly_fields = ()


class LoginView(SysConfContextMixin, TemplateResponseMixin, View):
    template_name = "admin/login.htm"

    def get(self, request, *args, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['form'] = LoginForm()
        context['errortip'] = None
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                return self.authenticate(cd['username'], cd['password'])
            except AuthenticateError as e:
                errortip = e.message
        else:
            errortip = u'用户名和密码不能为空，请输入。'

        context['form'] = LoginForm()
        context['errortip'] = errortip
        return self.render_to_response(context)

    def authenticate(self, username, password):
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise AuthenticateError(u'用户名或密码有误，请重新输入。')
        elif user.is_active == 0:
            raise AuthenticateError(u'用户名未激活，请联系管理员激活该用户。')
        else:
            auth.login(self.request, user)
            permissions = self.get_permissions(user)
            self.request.session[settings.PERMISSIONS_SESSION_KEY] = permissions
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    def get_permissions(self, user):
        mode = getattr(settings, 'AUTHENTICATION_MODE', 'local')

        print 'mode: ' + mode

        if mode == 'local':
            return self.get_local_permissions(user)
        else:
            return self.get_remote_permissions(user)

    def get_remote_permissions(self, user):
        backend_path = user.backend
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(user.backend)
            permissions = backend.get_permissions(user.id)
            return permissions
        else:
            return None

    def get_local_permissions(self, user):
        m = AuthPermissionModel()

        permissions = []
        if user.is_superuser == 1:
            print 'is_superuser 1'
            permissions = m.get_list_system()
        else:
            role_str = user.roles
            roles = role_str.split(',')
            permissions = m.get_list_groups(roles)
        return permissions


class PwdModifyView(UpdateView):
    template_name = "admin/modify_pwd.htm"
    form_class = PwdModifyForm
    form_admin_class = PwdModifyFormAdmin

    def get_init_form_data(self, pk, pks):
        user = self.request.user
        return {
            'user_id': user.id,
            'old_pwd': '',
            'new_pwd': '',
            'confirm_pwd': ''
        }

    def modify(self, cd):
        try:
            service = UserModel()
            service.modify_pwd(cd['user_id'], cd['old_pwd'], cd['new_pwd'])
        except RestfulApiError as e:
            raise SuspiciousOperation(e.message)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)
