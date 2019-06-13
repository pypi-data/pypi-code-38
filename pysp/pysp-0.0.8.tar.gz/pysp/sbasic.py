import datetime
import os
import re
import sys

from contextlib import contextmanager
from weakref import WeakValueDictionary


@contextmanager
def stderr_redirector(stream):
    old_stderr = sys.stderr
    sys.stderr = stream
    try:
        yield
    finally:
        sys.stderr = old_stderr


class SFile:
    @classmethod
    def mkdir(cls, fpath):
        if not os.path.exists(fpath):
            os.makedirs(fpath)

    @classmethod
    def to_file(cls, fpath, data):
        cls.mkdir(os.path.dirname(os.path.abspath(fpath)))
        with open(fpath, 'w') as fd:
            fd.write(data)

    @classmethod
    def read_all(cls, fpath):
        with open(fpath, 'r') as fd:
            return fd.read()

    @classmethod
    def readline(cls, fpath):
        with open(fpath, 'r') as fd:
            for line in fd:
                yield line
        # return ''


class SSingleton(type):
    _instances = {}  # WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(SSingleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SStamp:
    DB_DATETIME = '%Y-%m-%d %H:%M:%S'
    DB_DATE = '%Y-%m-%d'
    DATE_SEPERATERS = '.-_/'

    @classmethod
    def now(cls, form=DB_DATETIME):
        return datetime.datetime.now().strftime(form)


class SStrExpand:
    MAX_LOOP_COUNT = 30

    class Error(Exception):
        pass

    # Reference: https://stackoverflow.com/a/30777398
    @classmethod
    def environ_vars(cls, string, default=None, skip_escaped=False):
        """Expand environment variables of form $var and ${var}.
           If parameter 'skip_escaped' is True, all escaped variable references
           (i.e. preceded by backslashes) are skipped.
           Unknown variables are set to 'default'. If 'default' is None,
           they are left unchanged.
        """
        def replace_var(m):
            defvalue = m.group(0) if default is None else default
            # print(m.group(2), m.group(1))
            return os.environ.get(m.group(2) or m.group(1), defvalue)

        reval = (r'(?<!\\)' if skip_escaped else '') + r'\$(\w+|\{([^}]*)\})'
        return re.sub(reval, replace_var, string)

    @classmethod
    def config_vars(cls, config, string):
        def replace_var(m):
            value = config.get_value(m.group(2) or m.group(1), m.group(0))
            if type(value) is list:
                # Just valid one-dimensional list
                return ','.join([str(x) for x in value])
            elif type(value) is dict:
                raise SStrExpand.Error('No Rules for dict.')
            return str(value)

        if config is None:
            return string
        reval = r'@([\w.]+|\{([^}]*)\})'
        return re.sub(reval, replace_var, string)

    @classmethod
    def convert(cls, string, config=None):
        lpcnt = 0
        o_string = string
        while True:
            p_string = string
            string = cls.config_vars(config, cls.environ_vars(p_string))
            # print(p_string, string)
            if p_string == string:
                return string
            lpcnt += 1
            if lpcnt > cls.MAX_LOOP_COUNT:
                emsg = 'Infinite Repeat Error: {}'.format(o_string)
                raise cls.Error(emsg)
        return string
