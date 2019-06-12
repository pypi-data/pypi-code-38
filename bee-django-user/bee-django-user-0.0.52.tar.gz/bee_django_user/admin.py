# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserSN

class UserSNAdmin(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'start', 'end', 'is_used')

    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    list_display_links = ('id',)

# 注册时，在第二个参数写上 admin model
admin.site.register(UserSN, UserSNAdmin)
