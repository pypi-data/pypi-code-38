import logging

_LEVELS = {
    'all': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
}


def configure_arg_parser(args_parser) -> None:
    args_parser.add_argument('-l', '--log', help='Log level', default='debug', choices=['all', 'debug', 'info', 'warn', 'error', 'none'])


def configure_logger(env) -> None:
    assert env.log, env

    msg_fmt = '%(levelname)s %(asctime)s [%(name)s] %(message)s'

    if env.log == 'none':
        logging.disable(logging.CRITICAL)
    else:
        lev = _LEVELS.get(env.log, None)
        if lev is None:
            raise SystemExit('Invalid value for logging level: "{}". Use all,debug,info,warn,error.'.format(env.log))
        logging.basicConfig(level=lev, format=msg_fmt)

    logging.addLevelName(logging.CRITICAL, '!!!')
    logging.addLevelName(logging.ERROR, '!! ')
    logging.addLevelName(logging.WARNING, '!  ')
    logging.addLevelName(logging.INFO, '   ')
    logging.addLevelName(logging.DEBUG, '   ')
