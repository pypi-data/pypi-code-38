import logging
import json


logger = logging.getLogger(__name__)


def log(
    message: str,
    request_url: str,
    status_code: str,
    response: str,
    request_body: dict = None,
):

    dict = {
        "request_url": request_url,
        "status_code": status_code,
        "response": response,
    }
    if request_body:
        dict["request_body"] = str(request_body)
    logger.debug(message, extra=dict)
