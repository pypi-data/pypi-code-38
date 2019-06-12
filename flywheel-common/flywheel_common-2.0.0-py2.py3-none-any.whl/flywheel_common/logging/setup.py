from __future__ import print_function
import sys
import logging
import yaml
import time
import os
import warnings
import threading
from logging import handlers

from .json_formatter import JSONLogFormatter
from .extra_formatter import wrap_default_handler

log = logging.getLogger(__name__)

try:
    import gevent_inotifyx as inotify
    LIVE_RELOAD = True
except ImportError:
    LIVE_RELOAD = False
    warnings.warn('inotify not installed, live logging config reload not supported')

def init_flywheel_logging(config_file, handler=None, tag=None, quiet=False, print_extras=True):
    """Initialize the python logging hierarchy to watch a config file that specifies the logging levels of individual loggers"""

    def update_logging():
        try:
            with open(config_file, 'r') as fp:
                try:
                    log_config = yaml.safe_load(fp)
                except yaml.YAMLError as e:
                    logging.error(e)
                    print(e, file=sys.stderr)
                    log_config = {'logging_level': 'INFO'}
        except FileNotFoundError as e:
            logging.error(e)
            print(e, file=sys.stderr)
            log_config = {'logging_level': 'INFO'}
        handler.setLevel(log_config['logging_level'])
        if not quiet:
            log.info('Setting logging level of handler to %s', log_config['logging_level'])
        for named_logger in log_config.get('named_loggers', []):
            logging.getLogger(named_logger['name']).setLevel(named_logger['level'])

    def watch_file():
        fd = inotify.init()
        if not quiet:
            log.debug('Watching %s for changes', config_file)
        try:
            wd = inotify.add_watch(fd, os.path.dirname(config_file), inotify.IN_MODIFY | inotify.IN_CLOSE_WRITE)
            while True:
                for event in inotify.get_events(fd):
                    if not quiet:
                        log.debug('Got inotify event %s - %s', event.name, event.get_mask_description())
                    if event.name == os.path.basename(config_file):
                        update_logging()
        finally:
            os.close(fd)

    # Log extras on root level logger
    root = logging.getLogger()
    if print_extras:
        wrap_default_handler(root)

    if handler is None:
        syslog_host = os.getenv('SYSLOG_HOST', 'logger')
        syslog_port = int(os.getenv('SYSLOG_PORT', '514'))
        if not quiet:
            log.info('Sending syslogs to %s:%s', syslog_host, syslog_port)
        handler = logging.handlers.SysLogHandler(address=(syslog_host, syslog_port))
    formatter = JSONLogFormatter(tag=tag)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel('DEBUG')

    if not os.path.exists(config_file):
        if not quiet:
            log.error('No logging file configured')
        return

    update_logging()

    if LIVE_RELOAD:
        t = threading.Thread(target=watch_file)
        t.daemon = True
        t.start()
