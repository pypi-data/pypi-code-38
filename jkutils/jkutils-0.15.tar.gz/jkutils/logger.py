import json
import logging
import logging.handlers
import sys
import uuid
from threading import local as ThreadLocal

from jkutils.time import utc_strftime

try:
    from flask import g
except Exception:
    pass


CONSOLE_FORMAT = "%(message)s"
# ‘2006-01-02 15:04:05‘
DATEFMT = "%Y-%m-%d %H:%M:%S"
LEVEL = logging.INFO


if hasattr(sys, "_getframe"):
    currentframe = lambda: sys._getframe(3)
else:  # pragma: no cover

    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


class LogJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except Exception:
            return str(obj)


class LocalStorage:
    """
    本地存储
    """

    def __init__(self):
        self._fields = {}

    def get(self):
        return self._fields

    def add(self, **kwargs):
        """
        设置默认打印字段
        """
        self._fields.update(kwargs)

    def remove(self, *keys):
        """
        移除指定默认打印字段
        """
        for key in keys:
            if key in self._fields:
                self._fields.pop(key)

    def remove_all(self):
        """
        移除所有默认打印字段
        """
        self._fields = dict()


class FlaskGStorage:
    """
    通过 flask 中 g 对象存储
    """

    def get(self):
        try:
            if not hasattr(g, "log_default_fields"):
                return {}
            return g.log_default_fields
        except Exception:
            return {}

    def add(self, **kwargs):
        """
        设置默认打印字段
        """
        try:
            if not hasattr(g, "log_default_fields"):
                g.log_default_fields = {}
            g.log_default_fields.update(kwargs)
        except Exception:
            pass

    def remove(self, *keys):
        """
        移除指定默认打印字段
        """
        try:
            if not hasattr(g, "log_default_fields"):
                return
            for key in keys:
                if key in g.log_default_fields:
                    g.log_default_fields.pop(key)
        except Exception:
            pass

    def remove_all(self):
        """
        移除所有默认打印字段
        """
        try:
            if not hasattr(g, "log_default_fields"):
                return
            g.log_default_fields = dict()
        except Exception:
            pass


class ThreadLocalStorage:
    def __init__(self):
        self._local = ThreadLocal()

    """
    通过 ThreadLocal 存储
    """

    def get(self):
        if not hasattr(self._local, "log_default_fields"):
            return {}
        return self._local.log_default_fields

    def add(self, **kwargs):
        """
        设置默认打印字段
        """
        if not hasattr(self._local, "log_default_fields"):
            self._local.log_default_fields = {}
        self._local.log_default_fields.update(kwargs)

    def remove(self, *keys):
        """
        移除指定默认打印字段
        """
        if not hasattr(self._local, "log_default_fields"):
            return
        for key in keys:
            if key in self._local.log_default_fields:
                self._local.log_default_fields.pop(key)

    def remove_all(self):
        """
        移除所有默认打印字段
        """
        if not hasattr(self._local, "log_default_fields"):
            return
        self._local.log_default_fields = dict()


class JKLogger:
    def __init__(self, project_name, level=LEVEL, datefmt=DATEFMT, native=True, default_fileds_obj=LocalStorage()):
        self._name = project_name
        self._datefmt = datefmt
        self.default_fileds_obj = default_fileds_obj

        if native:
            logging.basicConfig(level=level)
            logging.debug = self.debug
            logging.info = self.info
            logging.warning = self.warning
            logging.warn = self.warn
            logging.error = self.error
            logging.critical = self.critical

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(fmt=CONSOLE_FORMAT))

        self._logger = logging.getLogger(project_name)
        self._logger.setLevel(level)
        self._logger.addHandler(console_handler)

        self._logger.propagate = False

    def debug(self, msg, **kw):
        self._log("debug", msg, **kw)

    def info(self, msg, **kw):
        self._log("info", msg, **kw)

    def warning(self, msg, **kw):
        self._log("warn", msg, **kw)

    def warn(self, msg, **kw):
        self._log("warn", msg, **kw)

    def error(self, msg, **kw):
        self._log("error", msg, **kw)

    def critical(self, msg, **kw):
        self._log("critical", msg, **kw)

    def _log(self, level, msg, **kw):
        f = currentframe()
        data = dict()
        data.update(self.default_fileds_obj.get())
        data.update(
            {
                "msg": msg,
                "funcname": f.f_code.co_name,
                "file": "{}:{}".format(f.f_code.co_filename, f.f_lineno),
                "level": level,
                "project": self._name,
                "time": utc_strftime(self._datefmt),
            }
        )
        data.update(kw)
        data = self.remove_empty_filed(data)
        getattr(self._logger, level)(json.dumps(data, cls=LogJSONEncoder, ensure_ascii=False))

    def remove_empty_filed(self, data):
        """
        去除空字段
        """
        return {k: v for k, v in data.items() if v != "" and v != None}

    def __getattr__(self, name):
        """其他方法透传"""
        return getattr(self._logger, name)

    def set_default_fields(self, **kwargs):
        """
        即将废弃
        """
        self.add(**kwargs)

    def remove_default_field(self, *keys):
        """
        即将废弃
        """
        self.remove(*keys)

    def remove_default_all_fields(self):
        """
        即将废弃
        """
        self.remove_all()

    def add(self, **kwargs):
        """
        设置默认打印字段
        """
        self.default_fileds_obj.add(**kwargs)

    def remove(self, *keys):
        """
        移除指定默认打印字段
        """
        self.default_fileds_obj.remove(*keys)

    def remove_all(self):
        """
        移除所有默认打印字段
        """
        self.default_fileds_obj.remove_all()

    @property
    def log_id(self):
        return uuid.uuid4().hex
