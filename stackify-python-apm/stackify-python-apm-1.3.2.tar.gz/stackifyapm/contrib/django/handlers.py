from __future__ import absolute_import

import logging
import sys
import warnings

from stackifyapm.handlers.exceptions import get_exception_context


logger = logging.getLogger("stackifyapm.logging")


def exception_handler(client, request=None, **kwargs):
    exc_info = sys.exc_info()
    try:
        if getattr(exc_info[1], "skip_stackifyapm", False):
            return

        client.capture_exception(
            exception=get_exception_context(exc_info[1], exc_info[2])
        )
    except Exception as exc:
        try:
            client.error_logger.exception(u"Unable to process log entry: {}".format(exc))
        except Exception as exc:
            warnings.warn(u"Unable to process log entry: {}".format(exc))
    finally:
        try:
            del exc_info
        except Exception as e:
            client.error_logger.exception(e)
