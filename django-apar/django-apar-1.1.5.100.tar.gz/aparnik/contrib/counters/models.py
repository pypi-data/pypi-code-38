# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.users.models import User
from aparnik.contrib.basemodels.models import BaseModel


# Create your models here.

class CounterManager(models.Manager):
    def get_queryset(self):
        return super(CounterManager, self).get_queryset()

    def active(self):
        return self.get_queryset()


class Counter(models.Model):
    # Action list performed by user
    # Add more actions as needed
    ACTION_VISIT = 'v'
    ACTION_SHARE = 's'
    ACTION_CHOICES = (
        (ACTION_VISIT, _('Visiting')),
        (ACTION_SHARE, _('Sharing')),
    )

    user_obj = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('User'))
    model_obj = models.ForeignKey(BaseModel, on_delete=models.CASCADE, verbose_name=_('Base Model'))
    action = models.CharField(choices=ACTION_CHOICES, max_length=2, verbose_name=_('Action kind'))
    create_date = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = CounterManager()

    def __str__(self):
        return str(self.model_obj)

    class Meta:
        verbose_name = _('Counter')
        verbose_name_plural = _('Counters')
