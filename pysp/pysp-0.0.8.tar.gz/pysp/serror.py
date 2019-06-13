# from __future__ import print_function
import logging
import os
# import sys

from inspect import getframeinfo, stack


_log = logging.getLogger('pysp')
_log.handlers = []
if 'DEBUG_PYTHON' in os.environ:
    _log_level = logging.DEBUG
    _log.setLevel(_log_level)
    h = logging.StreamHandler()
    h.setLevel(_log_level)
    _log.addHandler(h)
    # _log.propagate = 0

# _LOG_FORMAT = '%(asctime)s: %(message)s'
# _lhandler = logging.StreamHandler()
# _lhandler.setFormatter(logging.Formatter(_LOG_FORMAT))
# _log.addHandler(_lhandler)
# _log.propagate = 0


class Debug:
    DEBUG = False
    TAG_DEBUG = '[D] '
    TAG_ERROR = '[E] '
    TAG_INFO = '[I] '

    @classmethod
    def _print(cls, tag, *args):
        log_print = {
            cls.TAG_DEBUG: _log.debug,
            cls.TAG_ERROR: _log.error,
            cls.TAG_INFO: _log.info,
        }
        caller = getframeinfo(stack()[2][0])
        filename = os.path.basename(caller.filename)
        lmsg = f'{caller.lineno:4d}:{filename:<20}{tag} {" ".join(args)}'
        log_print.get(tag)(lmsg)


class SDebug(Debug):

    def dprint(self, *args, **kwargs):
        if self.DEBUG:
            self._print(self.TAG_DEBUG, *args)
            # _log.debug(f"{self.TAG_DEBUG} {' '.join(args)}")
            # print(self.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    def eprint(self, *args, **kwargs):
        self._print(self.TAG_ERROR, *args)
        # _log.error(f"{self.TAG_ERROR} {' '.join(args)}")
        # print(self.TAG_ERROR, *args, file=sys.stderr, **kwargs)

    def iprint(self, *args, **kwargs):
        self._print(self.TAG_INFO, *args)
        # _log.info(f"{self.TAG_INFO} {' '.join(args)}")
        # print(self.TAG_INFO, *args, file=sys.stderr, **kwargs)


class SCDebug(Debug):
    @classmethod
    def dprint(cls, *args, **kwargs):
        if cls.DEBUG:
            cls._print(cls.TAG_DEBUG, *args)
            # _log.debug(f"{cls.TAG_DEBUG} {' '.join(args)}")
            # print(cls.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    @classmethod
    def eprint(cls, *args, **kwargs):
        cls._print(cls.TAG_ERROR, *args)
        # _log.error(f"{cls.TAG_ERROR} {' '.join(args)}")
        # print(cls.TAG_ERROR, *args, file=sys.stderr, **kwargs)

    @classmethod
    def iprint(cls, *args, **kwargs):
        cls._print(cls.TAG_INFO, *args)
        # _log.info(f"{cls.TAG_INFO} {' '.join(args)}")
        # print(cls.TAG_INFO, *args, file=sys.stderr, **kwargs)


class SError(Exception):
    pass


if __name__ == '__main__':
    a = SCDebug()
    a.DEBUG = True
    a.iprint('INFO')
