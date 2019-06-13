import os
import argparse
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
import logging
import logging.config
import logging.handlers
import coloredlogs
import yaml
import requestlogger

import comring.webapp

LOGGER = logging.getLogger(__name__)

DEFAULT_LOG_CONF = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging-default.yaml')
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5500

def setup_logging(config_path=DEFAULT_LOG_CONF, default_level=logging.INFO, env_key='LOG_CFG'):
    path = config_path
    env_path = os.getenv(env_key, None)
    if env_path:
        path = env_path

    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                logging.error('Error setup logging', exc_info=e)
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        logging.warn('Failed to load log configuration. Using defaults')

def create_server(app, bind_host, bind_port):
    
    dispatcher = PathInfoDispatcher({'/': app})
    return WSGIServer((bind_host, bind_port), dispatcher)

def with_access_log(app, filepath=None, when='d', interval=7, **kwargs):
    if filepath is not None:
        handlers = [
            logging.handlers.TimedRotatingFileHandler(
                filepath, when, interval, **kwargs)
        ]
    else:
        handlers = [logging.StreamHandler()]
    return requestlogger.WSGILogger(app, handlers, requestlogger.ApacheFormatter())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default='127.0.0.1', help='Bind address')
    parser.add_argument('-p', '--port', type=int, default='5500', help='Bind port')
    parser.add_argument('-L', '--logconfig', help='Logging config file')
    parser.add_argument('-l', '--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING', help='Set log level')

    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.loglevel:
        lvl = getattr(logging, args.loglevel, None)
        if isinstance(lvl, int):
            loglevel = lvl

    logconfig = DEFAULT_LOG_CONF
    if args.logconfig:
        logconfig = args.logconfig

    setup_logging(config_path=logconfig, default_level=loglevel)

    app = comring.webapp.create_app()
    server = create_server(with_access_log(app),
            args.address or DEFAULT_HOST,
            args.port or DEFAULT_PORT)

    try:
        server.start()
        LOGGER.info('Server started: %s', server.bind_addr)
    except KeyboardInterrupt:
        server.stop()
