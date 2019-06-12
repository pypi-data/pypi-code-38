# -*- coding: utf-8 -*-
import os

from missinglink.core.api import ApiCaller


def monitor_logs(ctx, url, disable_colors):
    from missinglink.commands.sse_firebase import LogsThread

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', url)

    logs_thread = LogsThread(ctx.obj.config, result['url'], disable_colors)
    logs_thread.start()
    logs_thread.join()


# This env var is set on the windows Dockerfile.
# It is used to determine if to use the default gateway in order to connect to the docker host.
def is_windows_containers():
    return os.environ.get('ML_WINDOWS_CONTAINERS') is not None


def is_windows():
    return os.name == 'nt'
