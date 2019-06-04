# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_szuprefix.auth.signals import to_get_user_profile
from . import models, serializers


@receiver(post_save, sender=models.Party)
def initDepartmentAndManagerWorker(sender, **kwargs):
    if kwargs['created']:
        party = kwargs['instance']
        party.root_department
        party.manager_worker


@receiver(to_get_user_profile)
def get_worker_profile(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'as_saas_worker'):
        return serializers.CurrentWorkerSerializer(user.as_saas_worker, context=dict(request=kwargs['request']))
