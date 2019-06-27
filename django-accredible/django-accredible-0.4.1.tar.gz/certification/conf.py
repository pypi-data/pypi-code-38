    # python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class CertificationConfig(AppConf):
    APP_NAME = 'certification'

    CH_STATUS_PENDING = 'A'
    CH_STATUS_GENERATED = 'B'
    CH_STATUS_DEFAULT = CH_STATUS_PENDING
    CH_STATUS = (
        (CH_STATUS_PENDING, 'Pending'),
        (CH_STATUS_GENERATED, 'Generated'),
    )

    CH_GROUP_STATUS_DEFAULT = CH_STATUS_PENDING
    CH_GROUP_STATUS = (
        (CH_STATUS_PENDING, 'Pending'),
        (CH_STATUS_GENERATED, 'Generated'),
    )
