# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage


# Create your models here.
GRADE_FEILD_TEXT_ALIGN_CHOICES = (("left", '居左'), ("center", '居中'), ("right", '居右'))

original_cert = os.path.join(settings.EXAM_CERT_PATH, 'original')
icon = os.path.join(settings.EXAM_CERT_PATH, 'icon')
fs_cert = FileSystemStorage(location=original_cert, base_url="/" + original_cert)
fs_icon = FileSystemStorage(location=icon, base_url="/" + icon)


def get_user_table():
    return settings.AUTH_USER_MODEL


def get_user_name_field():
    return settings.USER_NAME_FIELD


class Grade(models.Model):
    name = models.CharField(max_length=180, verbose_name='考级名称')
    order_by = models.IntegerField(default=0, verbose_name='顺序', blank=True)
    is_show = models.BooleanField(default=True, verbose_name='是否显示', blank=True)
    notice = models.ForeignKey("bee_django_exam.Notice", verbose_name="考试须知", null=True, blank=True)
    cert_image = models.ImageField(storage=fs_cert, null=True, blank=True, verbose_name="证书图片")
    icon = models.ImageField(storage=fs_icon, null=True, blank=True, verbose_name='级别小图标')
    coin = models.IntegerField(verbose_name='考级消耗M币', default=0)

    class Meta:
        db_table = 'bee_django_exam_grade'
        app_label = 'bee_django_exam'
        ordering = ['order_by']
        permissions=(
            ('can_manage_exam', '可以进入考级管理页'),
            ('view_grade_list', '可以查看考级列表'),
        )

    def get_absolute_url(self):
        return reverse('bee_django_exam:grade_detail', kwargs={'pk': self.pk})

    def get_show_text(self):
        if self.is_show == False:
            return "否"
        elif self.is_show == True:
            return "是"

    def __unicode__(self):
        return (self.name)


class GradeCertField(models.Model):
    grade = models.ForeignKey("bee_django_exam.Grade")
    name = models.CharField(max_length=180)
    field = models.CharField(max_length=180)
    font_color = models.CharField(max_length=7, default="#000000", verbose_name='字体颜色')
    font_size = models.IntegerField(default=20, verbose_name='字体大小')
    text_width = models.IntegerField(verbose_name='文字区域宽度',help_text='文字超出此宽度时，会不显示多出的文字')
    text_height = models.IntegerField(verbose_name="文字区域高度",null=True,blank=True,help_text='单行文字时可不填写，多行文字时必填')
    text_post_x = models.IntegerField(verbose_name="文字区域左上角横坐标")
    text_post_y = models.IntegerField(verbose_name="文字区域左上角纵坐标")
    text_bg_color = models.CharField(max_length=7, verbose_name='文字区域背景颜色', null=True, blank=True,help_text='选填')
    text_align = models.CharField(max_length=180, verbose_name='文字对齐',help_text='文字在填写区域中的对齐方式')

    class Meta:
        db_table = 'bee_django_exam_grade_cert_field'
        app_label = 'bee_django_exam'
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('bee_django_exam:grade_cert_field_list')

    def __unicode__(self):
        return (self.name)


class Notice(models.Model):
    title = models.CharField(max_length=180, verbose_name='须知标题')
    context = models.TextField(verbose_name='须知内容', null=True, blank=True)
    is_require = models.BooleanField(verbose_name='是否必选', null=False,default=True)

    class Meta:
        db_table = 'bee_django_exam_notice'
        app_label = 'bee_django_exam'
        ordering = ['-id']
        permissions=(
            ('view_notice_list', '可以查看须知列表'),
        )

    def get_absolute_url(self):
        return reverse('bee_django_exam:notice_detail', kwargs={'pk': self.pk})

    # def get_require_text(self):
    #     if self.is_require == False:
    #         return "否"
    #     elif self.is_require == True:
    #         return "是"

    def __unicode__(self):
        return self.title


EXAM_STATUS_CHOICES = ((-1, "未报名"), (-2, "已报名"), (1, '通过'), (2, '未通过'), (3, '关闭'))


# 用户考级表
class UserExamRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bee_django_exam_user')
    grade = models.ForeignKey("bee_django_exam.Grade", related_name='bee_django_exam_grade', null=True,
                              on_delete=models.SET_NULL, verbose_name='考试级别')
    grade_name = models.CharField(max_length=180, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    status = models.IntegerField(choices=EXAM_STATUS_CHOICES, null=True, verbose_name="状态", blank=True, default=-1)
    is_passed = models.BooleanField(default=False, verbose_name='是否通过')
    passed_date = models.CharField(max_length=180, null=True, blank=True, verbose_name='通过日期')
    year = models.CharField(max_length=180, null=True, blank=True, verbose_name='年度')
    result = models.CharField(max_length=180, null=True, blank=True, verbose_name='成绩')
    info = models.TextField(verbose_name='其他', null=True, blank=True)
    cert = models.FilePathField(verbose_name='证书地址', null=True, blank=True)

    class Meta:
        db_table = 'bee_django_exam_user_exam_record'
        app_label = 'bee_django_exam'
        ordering = ['-created_at']
        permissions=(
            ('view_all_user_exam_record_list', '可以查看所有学生考级列表'),
            ('create_cert', '生成证书'),
        )

    def __unicode__(self):
        return ("UserExamRecord->name:" + self.pk.__str__())

    def get_status_text(self):
        for c in EXAM_STATUS_CHOICES:
            if self.status == c[0]:
                return c[1]
        return ""

    def get_passed_text(self):
        if self.is_passed == False:
            return ""
        elif self.is_passed == True:
            return "通过"


# 用户是否开启考级
class UserStartExam(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    is_start_exam = models.BooleanField(default=True)
    update_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bee_django_exam_user_start_exam'
        app_label = 'bee_django_exam'

    def __unicode__(self):
        return ("UserExam->name:" + self.pk.__str__())
