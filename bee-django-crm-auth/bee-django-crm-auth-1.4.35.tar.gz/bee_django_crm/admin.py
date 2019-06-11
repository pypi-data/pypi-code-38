# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RegCode

class RegCodeAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'reg_name', 'reg_code','used_at','used_preuser')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id',)

# 注册时，在第二个参数写上 admin model
admin.site.register(RegCode, RegCodeAdmin)
