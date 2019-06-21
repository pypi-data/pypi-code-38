# -*- coding: utf-8 -*-
import os

import six


def _get_log_token(ctx, url):
    from missinglink.core.api import default_api_retry
    from missinglink.core.api import ApiCaller

    def gen_url():
        result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', url, retry=default_api_retry())

        return result['url']

    return gen_url


def monitor_logs(ctx, url, disable_colors, top_records=None):
    if top_records is None:
        top_records = 50

    from missinglink.commands.sse_firebase import LogsThread

    logs_thread = LogsThread(_get_log_token(ctx, url), disable_colors, top_records)
    logs_thread.start()
    logs_thread.join()
    if logs_thread.exception:
        six.raise_from(logs_thread.exception, None)


# This env var is set on the windows Dockerfile.
# It is used to determine if to use the default gateway in order to connect to the docker host.
def is_windows_containers():
    return os.environ.get('ML_WINDOWS_CONTAINERS') is not None


def is_windows():
    return os.name == 'nt'
