# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-04-24 19:39'
import logging
import time
from json.decoder import JSONDecodeError

import requests
import stackprinter
from requests.exceptions import ReadTimeout, ConnectionError

logger = logging.getLogger("python_common_tools")


class IRequest:
    RETRY_TIMES = 3

    @classmethod
    def secure_requests_json(cls, url, method='get', timeout=10, log_err=False, retry_times=None, *args, **kwargs):
        retry = retry_times if retry_times else IRequest.RETRY_TIMES
        j = {}
        while True:
            try:
                if method == 'get':
                    response = requests.get(url, timeout=timeout, *args, **kwargs)
                else:
                    response = requests.post(url, timeout=timeout, *args, **kwargs)
                j = response.json()
                break
            except ReadTimeout as e:
                if log_err:
                    logger.error(stackprinter.format(e))
                time.sleep(2)
                retry -= 1
                if retry < 0:
                    break
                logger.error(f"url={url},kwargs={kwargs} ReadTimeout retrying {retry}")
            except ConnectionError as e:
                if log_err:
                    logger.error(stackprinter.format(e))
                time.sleep(2)
                retry -= 1
                if retry < 0:
                    break
                logger.error(f"url={url},kwargs={kwargs} ConnectionError retrying {retry}")
            except JSONDecodeError as e:
                if log_err:
                    logger.error(stackprinter.format(e))
                logger.error(f"text={response.text}")
                time.sleep(2)
                retry -= 1
                if retry < 0:
                    break
                logger.error(f"url={url},kwargs={kwargs} JSONDecodeError retrying {retry}")
        return j

    @classmethod
    def secure_requests(cls, url, method='get', timeout=10, log_err=False, retry_times=None, **kwargs):
        retry = retry_times if retry_times else IRequest.RETRY_TIMES
        response = None
        while True:
            try:
                if method == 'get':
                    response = requests.get(url, timeout=timeout, **kwargs)
                else:
                    response = requests.post(url, timeout=timeout, **kwargs)
                break
            except ReadTimeout as e:
                if log_err:
                    logger.error(stackprinter.format(e))
                time.sleep(2)
                retry -= 1
                if retry < 0:
                    break
                logger.error(f"url={url},kwargs={kwargs} ReadTimeout retrying {retry}")
            except ConnectionError as e:
                if log_err:
                    logger.error(stackprinter.format(e))
                time.sleep(2)
                retry -= 1
                if retry < 0:
                    break
                logger.error(f"url={url},kwargs={kwargs} ConnectionError retrying {retry}")
        return response


secure_requests_json = IRequest.secure_requests_json
secure_requests = IRequest.secure_requests
