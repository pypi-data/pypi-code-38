import sys
import time

import pythonjsonlogger.jsonlogger
import sanic
import sanic.worker
import sanic.server
import sanic.websocket
import dynaconf

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['build_logging_configuration', 'settings']

LOG_TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


settings = dynaconf.LazySettings(  # pylint: disable=invalid-name
    ENVVAR_PREFIX_FOR_DYNACONF='SANIC',
    ROOT_PATH_FOR_DYNACONF="settings/",
    SILENT_ERRORS_FOR_DYNACONF=False,
    ENV_FOR_DYNACONF='default'
)


def build_logging_configuration(app_name: str):
    return dict(
        version=1,
        disable_existing_loggers=False,
        loggers={
            "sanic.root": {
                "level": settings.get('LOG_LEVELS', {}).get("sanic.root", 'INFO'),
                "handlers": [settings.get('BASE_HANDLER', 'console')]
            },
            "sanic.error": {
                "level": settings.get('LOG_LEVELS', {}).get("sanic.error", 'INFO'),
                "handlers": [settings.get('BASE_HANDLER', 'console')],
                "propagate": True,
                "qualname": "sanic.error",
            },
            "sanic.access": {
                "level": settings.get('LOG_LEVELS', {}).get("sanic.access", 'INFO'),
                "handlers": [settings.get('ACCESS_HANDLER', 'access_console')],
                "propagate": True,
                "qualname": "sanic.access",
            },
            'sanic_service_utils': {
                "level": settings.get('LOG_LEVELS', {}).get('sanic_service_utils', 'INFO'),
                "handlers": [settings.get('BASE_HANDLER', 'console')],
                "propagate": True,
                "qualname": "sanic.access",
            },
            app_name: {
                "level": settings.get('LOG_LEVELS', {}).get(app_name, 'INFO'),
                "handlers": [settings.get('BASE_HANDLER', 'console')],
                "propagate": True,
                "qualname": "sanic.access",
            }
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stdout,
            },
            'json_console': {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": sys.stdout,
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": sys.stdout,
            },
            'json_log': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'json',
                'when': 'D',
                'backupCount': 1,
                'filename': settings.get('LOGFILE_PATH', './sanic.log')
            },
        },
        formatters={
            'json': {
                '()': 'sanic_service_utils.configuration.CasualJsonFormatter',
                'reserved_attrs': (
                    'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelno', 'lineno',
                    'module', 'server_time', 'msecs', 'message', 'msg', 'pathname', 'process', 'processName'
                    'relativeCreated', 'stack_info', 'thread', 'threadName', 'request'
                ),
                'format': "[%(asctime)s] %(message)s",
                'datefmt': settings.get('TIMESTAMP_FORMAT', LOG_TIMESTAMP_FORMAT),
                "json_ensure_ascii": False
            },
            "generic": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": f"[{settings.get('TIMESTAMP_FORMAT', LOG_TIMESTAMP_FORMAT)}]",
                "class": "logging.Formatter",
            },
            "access": {
                "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: %(request)s %(message)s %(status)d %(byte)d",
                "datefmt": f"[{settings.get('TIMESTAMP_FORMAT', LOG_TIMESTAMP_FORMAT)}]",
                "class": "logging.Formatter",
            },
        },
    )


class CasualJsonFormatter(pythonjsonlogger.jsonlogger.JsonFormatter):

    def process_log_record(self, log_record):
        """
        Overrided to rename time property
        """
        log_record['timestamp'] = log_record.pop('asctime')
        return log_record


class BetterHttpProtocol(sanic.server.HttpProtocol):

    def log_response(self, response):
        """
        Helper method provided to enable the logging of responses in case if
        the :attr:`HttpProtocol.access_log` is enabled.

        :param response: Response generated for the current request

        :type response: :class:`sanic.response.HTTPResponse` or
            :class:`sanic.response.StreamingHTTPResponse`

        :return: None
        """
        if self.access_log:
            extra = {"status": getattr(response, "status", 0)}

            if isinstance(response, sanic.response.HTTPResponse):
                extra["response_lenght"] = len(response.body)
            else:
                extra["response_lenght"] = -1

            extra["remote_address"] = "UNKNOWN"
            current_time = time.time()
            if self.request is not None:
                if self.request.ip:
                    extra["remote_address"] = self.request.ip

                extra["request_method"] = self.request.method
                extra['path'] = self.request.path
                extra['query'] = self.request.query_string
                extra['protocol'] = self.request.scheme
                extra['user_agent'] = self.request.headers.get('user-agent')
                extra['request_time'] = f"{current_time - self.request.get('__START_TIME__', current_time):.4f}"
            else:
                extra["request_method"] = ''
                extra['url'] = ''
                extra['path'] = ''
                extra['query'] = ''
                extra['protocol'] = ''
                extra['user_agent'] = ''
                extra['request_time'] = ''

            sanic.log.access_logger.info("", extra=extra)


class BetterWebsocketProtocol(BetterHttpProtocol, sanic.websocket.WebSocketProtocol):

    pass


class BetterGunicornWorker(sanic.worker.GunicornWorker):

    websocket_protocol = BetterWebsocketProtocol
    http_protocol = BetterHttpProtocol
