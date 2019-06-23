# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__description__ = '''
'''

import os
import sys
import logging

import profig
import logzero
import psutil

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)


def get_file_size(file_pth):
    try:
        return os.path.getsize(file_pth)
    except FileNotFoundError as _:
        return 0


def create_file(pth):
    """ just create an empty file"""
    err = None
    _dir, _ = os.path.split(pth)
    if _dir and not os.path.exists(_dir):
        os.makedirs(_dir)
    try:
        open(pth, 'wb')
    except Exception as _err:
        err = _err
    return err


class Conf(object):
    """ configs based on profig

    e.g.:
        pth = '/tmp/t.cfg'
        dat = {
            'log.enabled': True,
            'log.level': 10,
            'log.file_pth': '/tmp/test.log',
        }

        cfg = Conf(config_file=pth, dat=dat).cfg
    """

    def __init__(self, config_file, dat=None, enable_default_log=True):
        try:
            if not get_file_size(config_file):
                create_file(config_file)
            self._pth, t = os.path.split(config_file)
            self._cfg_name = t.split('.')[0]
        except Exception as _:
            self._pth = '/tmp'
            self._cfg_name = 'izen'

        self.cfg = profig.Config(config_file, encoding='utf-8')
        self.cfg.read()

        if enable_default_log:
            self.__spawn()

        if dat:
            self.__do_init(dat)

        if not os.path.exists(os.path.expanduser(config_file)):
            self.cfg.sync()
            # print('[init-cfg-file]: {}'.format(os.path.expanduser(pth)))
            # raise SystemExit('[init-cfg-file]: {}'.format(os.path.expanduser(pth)))

    def __spawn(self):
        dat = {
            'log.enabled': False,
            'log.file_pth': '{}/{}.log'.format(self._pth, self._cfg_name),
            'log.file_backups': 3,
            'log.file_size': 5,
            'log.level': 10,
            'log.symbol': '☰☷☳☴☵☲☶☱',
        }
        self.__do_init(dat)

    def __do_init(self, dat_dict):
        for k, v in dat_dict.items():
            if isinstance(v, dict):
                self.cfg.init(k, v['val'], v['proto'])
            else:
                self.cfg.init(k, v)
        self.cfg.sync()


class LFormatter(logzero.LogFormatter):
    """ overwrite logzero's LogFormatter

    - remove ``[]``, support customize `level indicator: e.g. ♨✔⊙✘◈`
    - add color for ``critical``

    """
    DEFAULT_FORMAT = '%(color)s {}%(levelname)1.1s %(asctime)s ' \
                     '%(module)s:%(lineno)d {}%(end_color)s %(' \
                     'message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: logzero.ForegroundColors.CYAN,
        logging.INFO: logzero.ForegroundColors.GREEN,
        logging.WARNING: logzero.ForegroundColors.YELLOW,
        logging.ERROR: logzero.ForegroundColors.RED,
        logging.CRITICAL: logzero.ForegroundColors.MAGENTA,
    }

    def __init__(self, log_pre='♨✔⊙✘◈', date_fmt=None):
        date_fmt = date_fmt or self.DEFAULT_DATE_FORMAT
        logzero.LogFormatter.__init__(self,
                                      datefmt=date_fmt,
                                      colors=self.DEFAULT_COLORS
                                      )
        system_icon = '' * 5 if psutil.MACOS else '' if psutil.LINUX else ''
        # if len(log_pre) < 5, the left chars will be blank
        log_pre += system_icon[len(log_pre):]
        self.CHAR_PRE = dict(zip(range(5), log_pre))

    def format(self, record):
        _char_pre = self.CHAR_PRE[record.levelno / 10 - 1] + ' '
        __fmt = self.DEFAULT_FORMAT
        __fmt = __fmt.format(_char_pre, '|')
        self._fmt = __fmt
        return logzero.LogFormatter.format(self, record)


class ICfg(object):
    def __init__(self, config_file, dat):
        self.cfg = {}
        self.zlog = logzero
        self._spawn(config_file, dat)

    def _spawn(self, config_file, dat):
        self.cfg = Conf(
            config_file=config_file,
            dat=dat,
        ).cfg
        logzero.formatter(
            LFormatter(log_pre=self.cfg.get('log.symbol', ''))
        )
        logzero.loglevel(self.cfg.get('log.level', 20))
        self.zlog = logzero.logger
