from tornado.options import define
import logging

define('debug', default=True, type=bool, help='Work in debug mode')
define('port', default=7777, type=int, help='Port to run on')
define('host', default='127.0.0.1', help='Host to run on')

define('dns_resolver', default='tornado.platform.caresresolver.CaresResolver', help='DNS resolver')

define('log_filename', default='/tmp/mockry.log', help='Log filename')
define('log_level', default=logging.DEBUG, help='Log level')

define('config', default='example.json', help='Path to application file')

define('options', default=None, help='Path to configuration file')
