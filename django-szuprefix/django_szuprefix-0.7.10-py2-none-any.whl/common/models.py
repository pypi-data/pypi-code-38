# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_szuprefix.utils.modelutils import JSONField


class Setting(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "配置"
        unique_together = ("content_type", "object_id", "name")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField("名称", max_length=64, null=False, blank=False)
    json_data = JSONField("内容", blank=True, null=True)

    def __unicode__(self):
        return "%s.%s" % (self.content_object, self.name)


class Attachment(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "附件"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.FileField("文件", upload_to="attachments/%Y/%m/%d/")
    name = models.CharField("文件名", null=True, blank=True, max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True,
                              related_name="common_attachments")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s.attachments.%s" % (self.content_object, self.file)


class TempFile(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "临时文件"
        ordering = ('-create_time',)

    file = models.FileField("文件", upload_to="tempfile/%Y/%m/%d/")
    name = models.CharField("文件名", blank=True, max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True,
                              related_name="common_tempfiles")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def save(self, **kwargs):
        if not self.name:
            self.name = unicode(self.file)
        return super(TempFile, self).save(**kwargs)

    def __unicode__(self):
        return self.name


class Image(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "图片"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.ImageField("文件", upload_to="images/%Y/%m/%d/")
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="common_images")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    def __unicode__(self):
        return "%s.images.%s" % (self.content_object, self.file)


class Event(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "事件"
        ordering = ('-create_time',)

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField("名称", max_length=64)
    context = JSONField("上下文", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __unicode__(self):
        return "%s.%s@%s" % (self.content_object, self.name, self.create_time.isoformat())


class Trash(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "垃圾"
        unique_together = ("content_type", "object_id")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_name = models.CharField("名称", max_length=256, null=True, blank=True)
    json_data = JSONField("内容", blank=True, null=True)
    create_time = models.DateTimeField("删除时间", auto_now_add=True)

    def __unicode__(self):
        return "%s.%s" % (self.content_type, self.object_id)


class VersionHistory(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "版本历史"
        unique_together = ("content_type", "object_id", "version")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, null=True, blank=True)
    version = models.PositiveIntegerField()
    json_data = JSONField("内容", blank=True, null=True)
    create_time = models.DateTimeField("更新时间", auto_now_add=True)

    def __unicode__(self):
        return "%s.%s.V%d" % (self.content_type, self.object_id, self.version)

    def recover(self):
        obj = self.content_object
        m = obj._meta
        from django.db.models.fields.related import ForeignKey
        data = self.json_data
        for f in m.fields:
            fn = f.name
            v = data.get(fn)
            if isinstance(f, ForeignKey):
                fn = "%s_id" % fn
            setattr(obj, fn, v)
        obj.save()


class ExcelTask(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "Excel导出任务"

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    name = models.CharField("名称", max_length=128, null=False, blank=False)
    params = JSONField("参数")
    status = models.PositiveSmallIntegerField("状态", choices=((0, "等待执行"), (1, "开始执行"), (2, "执行中"), (4, "执行完毕")),
                                              default=0)
    owner = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="common_excel_tasks")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    attachments = GenericRelation(Attachment)

    def __unicode__(self):
        return "%s.tasks.%s" % (self.content_object, self.name)
