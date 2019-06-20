# -*- coding: utf-8 -*-
from congo.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as DjModelBackend

class ModelBackend(DjModelBackend):
    def authenticate(self, username = None, password = None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            if username and "@" not in username:
                user = UserModel.objects.get(email = "%s@%s" % (username, settings.CONGO_AUTHENTICATION_DOMAIN))
                if user.check_password(password):
                    return user
            else:
                return None
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            UserModel = get_user_model()
            return UserModel._default_manager.get(pk = user_id)
        except UserModel.DoesNotExist:
            return None
