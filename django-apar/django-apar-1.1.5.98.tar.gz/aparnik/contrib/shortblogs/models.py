# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class ShortBlogManager(models.Manager):
    def get_queryset(self):
        return super(ShortBlogManager, self).get_queryset().order_by('-id')


class ShortBlog(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = ShortBlogManager()

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(ShortBlog, self).__init__(*args, **kwargs)

    # class Meta:
    #     verbose_name = 'خبر'
    class Meta:
        verbose_name = _('Short Blog')
        verbose_name_plural = _('Short Blogs')

