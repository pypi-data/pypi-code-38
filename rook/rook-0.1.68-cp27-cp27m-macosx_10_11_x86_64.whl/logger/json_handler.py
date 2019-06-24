import collections
import logging
import traceback

from backend.management.log_sender import sender


class JsonHandler(logging.Handler):
    TAGS = "backend"

    def __init__(self):
        super(JsonHandler, self).__init__()

    def close(self):
        pass

    def emit(self, record):
        sender.send(self._build_log(record), self.TAGS)

    def _build_log(self, record):
        data = {
            'name': self.get_name(),
            'msg': record.getMessage(),
            'formatted_message': record.getMessage(),
            'args': record.args,
            'level_name': record.levelname,
            'level_no': record.levelno,
            'path_name': record.pathname,
            'filename': record.filename,
            'module': record.module,
            'lineno': record.lineno,
            'function': record.funcName,
            'time': record.created,
            'thread_id': record.thread,
            'thread_name': record.threadName,
            'process_name': record.processName,
            'process_id': record.process,
            'traceback': traceback.format_exc(),
        }
        if hasattr(record, "rookout_extra"):
            for k, v in record.rookout_extra.items():
                data[k] = v
        return data
