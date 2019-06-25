# -*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend

__author__ = 'denishuang'
from . import models

class MobileBackend(ModelBackend):
    """
    Custom auth backend that uses an worker mobile and password
    """

    def authenticate(self, username, password):
        qset = models.Person.objects.filter(mobile=username)
        if qset.count() != 1:
            return
        person = qset.first()
        user = person.user
        if user.check_password(password) and user.is_active:
            return user
