import logging as logger
import time

import requests


def get_host_ip(reflect_service, service_name):
    if not reflect_service:
        raise Exception("REFLECT_SERVICE is None.")

    logger.info("Getting service registration address...")

    url = "{}?service={}".format(reflect_service, service_name)
    response = requests.get(url, timeout=10)
    if not response.status_code == 200:
        raise Exception("Request incorrect: <{}>".format(url))

    data = response.json()
    host, port = data["host"], data["port"]
    if host:
        host_ip = "{}:{}".format(host, port)
        logger.info("Getting success <{}>".format(host_ip))
        return host_ip

    logger.info("Getting failed <{}>, Retry after 3 second...".format(url))
    time.sleep(3)
    return get_host_ip(reflect_service, service_name)
