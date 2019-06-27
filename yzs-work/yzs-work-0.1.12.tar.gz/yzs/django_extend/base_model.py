from django.db import models
import uuid


class ActiveObjectsManager(models.Manager):
    """
    只查询enabled为True的对象
    """

    def get_queryset(self):
        return super(ActiveObjectsManager, self).get_queryset().filter(enabled=True)


class BaseModel(models.Model):
    """
    默认模型
    """
    object_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priority = models.IntegerField(default=0, verbose_name='对象的优先级')
    enabled = models.BooleanField(default=True, verbose_name='是否启用')

    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True, editable=False)

    objects = models.Manager()  # 全部对象管理器
    active_objects = ActiveObjectsManager()  # 所有激活状态的查询集合管理器

    class Meta:
        abstract = True

    def __str__(self):
        name = getattr(self, 'name', '')
        class_name = self._meta.verbose_name if self._meta.verbose_name else self.__class__.__name__

        return f"<{class_name}:{name+':' if name else self.pk}>"

    def delete(self, using=None, keep_parents=False, real_delete=False):
        """
        软删除逻辑
        """
        if not real_delete:
            self.enabled = False
            self.save()
        else:
            super(BaseModel, self).delete(using=using, keep_parents=keep_parents)
