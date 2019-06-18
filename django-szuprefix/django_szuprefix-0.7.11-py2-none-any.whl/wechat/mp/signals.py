import django.dispatch
import logging
from django.conf import settings

log = logging.getLogger('django.request')

token_updated = django.dispatch.Signal(providing_args=["token"])
pay_result_notice = django.dispatch.Signal(providing_args=["result"])
message_notice = django.dispatch.Signal(providing_args=["user", "message", "extra_info"])
