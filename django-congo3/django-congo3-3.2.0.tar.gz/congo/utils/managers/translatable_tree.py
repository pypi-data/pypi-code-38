# -*- coding: utf-8 -*-
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from parler.managers import TranslatableManager, TranslatableQuerySet

class TranslatableTreeQuerySet(TranslatableQuerySet, TreeQuerySet):
    pass

class TranslatableTreeManager(TreeManager, TranslatableManager):
    queryset_class = TranslatableTreeQuerySet

    def get_queryset(self):
        # This is the safest way to combine both get_queryset() calls
        # supporting all Django versions and MPTT 0.7.x versions
        return self.queryset_class(self.model, using = self._db).order_by(self.tree_id_attr, self.left_attr)

class TranslatableTreeVisibleManager(TranslatableTreeManager):
    def get_queryset(self):
        return super(TranslatableTreeVisibleManager, self).get_queryset().filter(is_visible = True)
