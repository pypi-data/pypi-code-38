# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import receiver

from ..auth.signals import to_get_user_profile
from . import serializers


@receiver(to_get_user_profile)
def get_wechat_profile(sender, **kwargs):
    user = kwargs['user']
    if hasattr(user, 'as_wechat_user'):
        return serializers.UserSerializer(user.as_wechat_user, context=dict(request=kwargs['request']))
