# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_szuprefix.utils.modelutils import CodeMixin

from django_szuprefix_saas.saas.models import Party
from django_szuprefix_saas.exam.models import Paper

class Category(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "类别"
        unique_together = ('party', 'code')
        ordering = ('party', '-create_time')

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="course_categories",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=256)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return self.name


class Course(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "课程"
        unique_together = ('party', 'name')
        ordering = ('party', '-create_time')
        permissions = (
            ("view_all_course", "查看所有课程"),
            ("view_course_sensitivity", "查看课程敏感信息")
        )

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="course_courses",
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=256)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    category = models.ForeignKey(Category, verbose_name=Category._meta.verbose_name, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)
    is_active = models.BooleanField("有效", blank=False)
    exam_papers = models.ManyToManyField(Paper, verbose_name=Paper._meta.verbose_name, blank=True, related_name="course_courses")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if self.is_active is None:
            self.is_active = True
        super(Course, self).save(**kwargs)


class Chapter(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "章节"
        unique_together = ('party', 'course', 'name')
        order_with_respect_to = 'course'

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="course_chapters",  on_delete=models.PROTECT)
    course = models.ForeignKey(Course, verbose_name=Course._meta.verbose_name, related_name="chapters",  on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=256)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    order_num = models.PositiveIntegerField("序号", default=0, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)
    exam_papers = models.ManyToManyField(Paper, verbose_name=Paper._meta.verbose_name, blank=True, related_name="course_chapters")

    def __unicode__(self):
        return self.name
