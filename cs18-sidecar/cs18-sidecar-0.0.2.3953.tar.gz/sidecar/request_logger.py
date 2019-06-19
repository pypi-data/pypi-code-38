from logging import Logger
from time import time
from typing import List, Callable

from flask import Flask, request, request_started, request_finished


class RequestLogger:
    def __init__(self, app: Flask, logger: Logger, route_black_list: List[Callable]):
        self.logger = logger
        self.route_black_list = [f.__name__ for f in route_black_list]
        request_started.connect(self.app_request_started, app)
        request_finished.connect(self.app_request_ended, app)

    # Flask Events

    def app_request_started(self, sender, **extra):
        setattr(request, "start_time", time())

    def app_request_ended(self, sender, response, **extra):
        if request.endpoint in self.route_black_list and 200 <= response.status_code < 300:
            return
        self.log_request_ended(response)

    # Logging Methods

    def log_request_ended(self, response):
        if not hasattr(request, 'logged'):
            duration = self._get_duration()
            self.logger.info(msg=self._get_log_message(response.status_code, duration),
                             extra=self._get_log_fields(response.status_code, duration))
        setattr(request, 'logged', True)

    def log_request_failed(self, exception: Exception, status: int):
        if not hasattr(request, 'logged'):
            duration = self._get_duration()
            self.logger.error(msg=self._get_log_message(status, duration),
                              extra=self._get_log_fields(status, duration),
                              exc_info=exception)
        setattr(request, 'logged', True)

    def _get_duration(self) -> int:
        return time() - getattr(request, "start_time")

    def _get_log_message(self, http_status: int, duration: int):
        func_str = ''
        if request.endpoint:
            args = ''
            if request.view_args:
                args = ", ".join([str(v) for (k, v) in request.view_args.items()])
            func_str = request.endpoint + "(" + args + ")"
        return "Response {0} ({1:.3f} sec) - {2}".format(http_status, duration, func_str or "Bad Url: " + request.url)

    def _get_log_fields(self, status: int, duration: int):
        return {
            "colony.request.ip": request.remote_addr,
            "colony.request.url": request.url,
            "colony.request.body": str(request.data),
            "colony.response.duration": duration,
            "colony.response.statuscode": status
        }
