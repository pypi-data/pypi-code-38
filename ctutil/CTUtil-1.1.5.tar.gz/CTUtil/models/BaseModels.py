from django.db import models


class BaseField(models.Model):

    createtime = models.DateTimeField('创建时间', auto_now_add=True)
    modifytime = models.DateTimeField('修改时间', auto_now=True)
    remark = models.CharField('备注', max_length=32, null=True, default=None, blank=True)

    class Meta:
        abstract = True
