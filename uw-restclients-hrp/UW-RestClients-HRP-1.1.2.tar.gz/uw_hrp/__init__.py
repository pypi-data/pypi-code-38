"""
This is the interface for interacting with
the hrp web service.
"""

import logging
from uw_hrp.dao import HRP_DAO
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def get_resource(url):
    response = HRP_DAO().getURL(url, {'Accept': 'application/json'})

    logger.debug("{0} ==status==> {1}".format(url, response.status))
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("{0} ==data==> {1}".format(url, response.data))
    return response.data
