"""
This module directly interacts with Bridge web services on
It will log the https requests and responses.
Be sure to set the logging configuration if you use the LiveDao!
"""

import logging
from restclients_core.exceptions import DataFailureException
from uw_bridge.dao import Bridge_DAO


logger = logging.getLogger(__name__)
DHEADER = {"Content-Type": "application/json",
           'Accept': 'application/json'}
GHEADER = {'Accept': 'application/json'}
PHEADER = {"Content-Type": "application/json",
           'Accept': 'application/json',
           'Connection': 'keep-alive'}


def delete_resource(url):
    response = Bridge_DAO().deleteURL(url, DHEADER)
    req_data = "DELETE {0}".format(url)
    _log_resp(req_data, response)

    if response.status != 204:
        # 204 is a successful deletion
        _raise_exception(req_data, url, response)

    return response


def get_resource(url):
    response = Bridge_DAO().getURL(url, GHEADER)
    req_data = "GET {0}".format(url)
    _log_resp(req_data, response)

    if response.status != 200:
        _raise_exception(req_data, url, response)

    return response.data


def patch_resource(url, body):
    """
    Patch resource with the given json body
    :returns: http response data
    """
    response = Bridge_DAO().patchURL(url, PHEADER, body)
    req_data = "PATCH {0}: {1}".format(url, body)
    _log_resp(req_data, response)

    if response.status != 200:
        _raise_exception(req_data, url, response)

    return response.data


def post_resource(url, body):
    """
    Post resource with the given json body
    :returns: http response data
    """
    response = Bridge_DAO().postURL(url, PHEADER, body)
    req_data = "POST {0}: {1}".format(url, body)
    _log_resp(req_data, response)

    if response.status != 200 and response.status != 201:
        _raise_exception(req_data, url, response)

    return response.data


def put_resource(url, body):
    """
    Update the entire resource
    Bridge PUT seems to have the same effect as PATCH currently.
    """
    pass


def _log_resp(req_data, response):
    logger.debug(" {0} ===> STATUS: {1:d}, DATA: {2}".format(
        req_data, response.status, response.data))


def _raise_exception(req_data, url, response):
    if response.status == 404:
        logger.warning(" {0} ===> {1}".format(req_data, response.status))
    else:
        logger.error(" {0} ===> {1}, {2}".format(
            req_data, response.status, response.data))
    raise DataFailureException(url, response.status, response.data)
