# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from django.contrib.auth.models import User


class UserAdmin(OldUserAdmin):
    readonly_fields = OldUserAdmin.readonly_fields + ('tmp_login_token',)
    fieldsets = OldUserAdmin.fieldsets + (('临时密码', {'fields': ('tmp_login_token',)}),)

    def tmp_login_token(self, user):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt=user.username)
        return signer.sign(user.id)

    tmp_login_token.short_description = "临时登录密码"
    tmp_login_token.help_text = "有效期5分钟"


def add_tmp_token_to_user_admin():
    admin.site.unregister(User)
    admin.site.register(User, UserAdmin)
