# -*- coding:utf-8 -*- 

from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
   class Meta:
        model = models.User
        fields = ('headimgurl', 'nickname', 'sex', 'province', 'city')

