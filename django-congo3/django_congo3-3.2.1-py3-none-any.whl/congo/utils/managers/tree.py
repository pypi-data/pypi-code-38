# -*- coding: utf-8 -*-
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet

class TreeVisibleManager(TreeManager):
    def get_queryset(self):
        return super(TreeVisibleManager, self).get_queryset().filter(is_visible = True)
