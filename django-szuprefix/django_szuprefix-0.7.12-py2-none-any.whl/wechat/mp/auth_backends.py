import logging

log = logging.getLogger("django")

from django.contrib.auth.backends import ModelBackend
from . import helper

class WeiXinBackend(ModelBackend):
    """
    Custom auth backend that uses an email address and password

    For this to work, the User model must have an 'email' field
    """

    def authenticate(self, code):
        md = helper.api.login(code)
        if 'errcode' in md:
            log.error("WeiXinBackend.authenticate error, data: %s" % md)
            return
        return helper.api.get_or_create_user(md).user
