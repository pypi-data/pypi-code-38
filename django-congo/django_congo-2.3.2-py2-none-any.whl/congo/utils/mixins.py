# -*- coding: utf-8 -*-
from django.db import models

class PositionMixin(models.Model):
    """
    Mixin dodający możliwość ustawiania obiektów w kolejności z poziomu admina. Dodaje nowe pole `position`.
    """

    position = models.IntegerField(u"#", blank = True, null = True)

    class Meta:
        abstract = True
        ordering = ("position",)

    def _set_position(self, manager):
        if self.position is None:
            try:
                self.position = manager.values_list('position', flat = True).order_by('-position')[0] + 1
            except (IndexError, TypeError):
                self.position = 0

    def save(self, *args, **kwargs):
        self._set_position(self.__class__.objects)
        return super(PositionMixin, self).save(*args, **kwargs)

