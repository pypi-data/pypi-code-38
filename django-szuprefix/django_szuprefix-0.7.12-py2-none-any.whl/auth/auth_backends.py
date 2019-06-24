# -*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend


class TempTokenBackend(ModelBackend):
    """
    Custom auth backend that uses an worker mobile and password
    """

    def authenticate(self, username, password):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt=username)
        try:
            uid = signer.unsign(password, max_age=300)
        except Exception, e:
            return
        from django.contrib.auth import models
        return models.User.objects.filter(username=username, id=uid).first()
