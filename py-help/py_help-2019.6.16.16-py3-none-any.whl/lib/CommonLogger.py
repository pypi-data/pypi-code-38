# -*- coding: utf-8 -*-
import logbook
import traceback
import better_exceptions
import re
from logbook import lookup_level
from logbook.more import ColorizedStderrHandler
from .path_helper import PathHelper
import copy
import os
import sys  # reload()之前必须要引入模块

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')

logbook.set_datetime_format("local")


def from_utf8(string):
    try:
        return string.decode('utf-8')
    except AttributeError:
        return string


def to_utf8(string):
    try:
        if sys.version_info < (3, 0):
            return string.encode('utf-8')
        else:
            return string
    except AttributeError:
        return to_utf8(str(string))
    except UnicodeDecodeError:
        try:
            return to_utf8(unicode(string, 'utf-8'))
        except UnicodeDecodeError:
            return string


class MyStderrHandler(ColorizedStderrHandler):
    pass


class CommonLogger(logbook.Logger):
    """
    所有的日志都通过这个类进行输出
    """

    loggers = {}
    handlers = {
        'all': [
        ],
    }
    handlers_init = False
    log_cfg = [
        {
            'name': 'default',
            'file_regex': '.*',
            'out_file': 'default.log',
            'log_level': 'info',
            'stderr_log_level': 'info',
            'stderr_log': False,
        },
        {
            'name': 'py_help_log',
            'file_regex': '.*py_help.*',
            'out_file': 'py_help.log',
            'log_level': 'debug',
            'stderr_log_level': 'debug',
            'stderr_log': True,
        },
    ]
    log_path = None

    @classmethod
    def set_log_path(cls, log_path):
        cls.log_path = log_path

    @classmethod
    def set_log_level(cls, cfg_name, level):
        for index, cfg in enumerate(cls.log_cfg):
            if cfg['name'] == cfg_name:
                cfg['log_level'] = level

    @classmethod
    def add_log_cfg(cls, log_cfg):
        cls.log_cfg.append(log_cfg)
        cls.__handlers_init(True)
        pass

    @staticmethod
    def common_log_format(record, handler):
        if record.calling_frame:
            log_frame = getattr(handler, 'log_frame')
            if log_frame is None:
                log_frame = 2
            target_frame = record.calling_frame.f_back
            for cnt in range(log_frame):
                target_frame = target_frame.f_back
            file_name = target_frame.f_code.co_filename
            func_name = target_frame.f_code.co_name
            file_line = target_frame.f_lineno
        else:
            file_name = "not support fname"
            func_name = ''
            file_line = "0"

        log = "[{time}][{level}][pid:{pid}][th:{thread}] \"{file}:{line}:[{func}]\": {msg}".format(
            level=record.level_name[0],
            msg=to_utf8(record.message),
            thread=record.thread,
            pid=os.getpid(),
            file=file_name,
            func=func_name,
            line=file_line,
            time=record.time,
        )

        if record.formatted_exception:
            log += "\n" + record.formatted_exception
        return log

    @classmethod
    def get_log_path(cls):
        if cls.log_path is None:
            cls.log_path = PathHelper.get_project_log()
        if not os.path.exists(cls.log_path):
            os.makedirs(cls.log_path)
        return cls.log_path

    @classmethod
    def __handlers_init(cls, force=False):
        if force or not cls.handlers_init:
            for cfg in cls.log_cfg:
                cfg_name = cfg.get('name')
                one_handle_arr = cls.handlers.get(cfg_name)
                if one_handle_arr is None:
                    cls.handlers[cfg_name] = []
                    # print("init handler {} {}".format(cfg_name, cfg))
                    if cfg.get('stderr_log'):
                        # bubble 意思是要不要传递到下一个handler处理,如果是false就不传递,这里必须是true的,否则下一个handler会失效
                        cls.handlers[cfg_name].append(
                            ColorizedStderrHandler(bubble=True, level=cfg.get('stderr_log_level', 'INFO').upper()))
                    if cfg.get('out_file', None) is not None:
                        # print("out file {} {} ".format(cls.get_log_path(), cfg.get('out_file', None)))
                        # bubble 意思是要不要传递到下一个handler处理,如果是false就不传递,这里必须是true的,否则下一个handler会失效
                        cls.handlers[cfg_name].append(logbook.TimedRotatingFileHandler(
                            os.path.join(cls.get_log_path(), cfg.get("out_file")),
                            date_format='%Y-%m-%d', encoding="utf-8", backup_count=3,
                            bubble=True))
            for handler_name, handlers in cls.handlers.items():
                for one_handle in handlers:
                    # print("init {} handler format {}".format(handler_name, one_handle))
                    one_handle.formatter = cls.common_log_format
            cls.handlers_init = True
            cls.loggers.clear()

    @classmethod
    def get_logger(cls, name=__file__, log_frame=2):
        cls.__handlers_init()
        if cls.loggers.get(name, None) is None:
            cls.loggers[name] = CommonLogger(name)
            # 其他的handlers就用正则来匹配
            for cfg in cls.log_cfg:
                cfg_name = cfg['name']
                the_reg = re.compile(cfg['file_regex'], re.I)
                if the_reg.match(name):
                    cls.loggers[name].level = lookup_level(cfg['log_level'].upper())
                    # 这里是必须要删掉的，因为需要顺序靠后的顶掉顺序考前的
                    del (cls.loggers[name].handlers[:])
                    for one_handle in cls.handlers[cfg_name]:
                        the_handler = copy.copy(one_handle)
                        the_handler.log_frame = log_frame
                        # print("append  logger {} handler:{}".format(name, the_handler))
                        cls.loggers[name].handlers.append(the_handler)
            # all里面的 handlers 就是都要的handlers吧
            for one_handle in cls.handlers['all']:
                cls.loggers[name].handlers.append(one_handle)
        return cls.loggers.get(name)

    def process_record(self, record):
        logbook.Logger.process_record(self, record)
        record.extra['cwd'] = os.getcwd()


def __log_msg(msg, level, es, frame_level=2):
    default_exc_msg = ''
    frame = sys._getframe(frame_level)
    code = frame.f_code
    # print("the fname::{}".format(code.co_filename))
    logger = CommonLogger.get_logger(code.co_filename, frame_level)
    try:
        # print("====file{} oh handlers:{}=======".format(code.co_filename, logger.handlers))
        if es is not None:
            default_exc_msg = traceback.format_exc()
            e_type, value, e_traceback = sys.exc_info()
            msg += "\n" + better_exceptions.format_exception(e_type, value, e_traceback)
        eval("logger.{level}(msg)".format(level=level))
    except Exception as aes:
        try:
            logger.error("logmsg get err :{}\n===========\n{}".format(aes.message, default_exc_msg))
        except Exception as fuck_ex:
            logger.error("怎么都写不下来消息==>{}".format(fuck_ex.message))


def set_log_path(log_path):
    CommonLogger.set_log_path(log_path)


def debug(msg, es=None, frame=2):
    __log_msg(msg, "debug", es, frame)


def info(msg, es=None, frame=2):
    __log_msg(msg, "info", es, frame)


def warn(msg, es=None, frame=2):
    __log_msg(msg, "warning", es, frame)


def error(msg, es=None, frame=2):
    __log_msg(msg, "error", es, frame)


def print_ex(ex):
    result = ''
    e_type = None
    value = None
    try:
        if ex is not None:
            e_type, value, e_traceback = sys.exc_info()
            result += "\n" + better_exceptions.format_exception(e_type, value, e_traceback)
    except Exception as aes:
        result += "\nprint_ex format_err: {}".format(aes.message)
        if ex is not None:
            result += "\norig ex: {},{}".format(e_type, value)
    return result


add_log_cfg = CommonLogger.add_log_cfg
set_log_level = CommonLogger.set_log_level
