# no handler is added
rootlogger = logging.getLogger()

def logger(name,
        level='debug',
        add_default_handler=False,
    ):
    """
    For logging in modules outside of nao use::
    log = nao.logger(__name__)
    """
    # process dict config

    # not necessary since Python2.7 accept string levels
    levels = {
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    lvl = levels[level.lower()]

    log = logging.getLogger(name)
    log.setLevel(lvl)

    # optional only if there is no other logger
    if add_default_handler:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        fmtr = logging.Formatter('{levelname:1s} {message:s}', style='{')
        ch.setFormatter(fmtr)
        log.addHandler(ch)

    log.root = rootlogger

    return log

# default logger for nao
log = logger(__name__, 'debug', True)