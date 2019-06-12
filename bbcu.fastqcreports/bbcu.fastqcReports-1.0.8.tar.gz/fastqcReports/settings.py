import os

PACKAGE_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(PACKAGE_ROOT, os.pardir))
PROJECT_NAME = os.path.basename(PACKAGE_ROOT)
# logging
DEFAULT_LOG_DIR = os.path.abspath('/tmp')

# TODO: move to use a dictConfig()
# LOG_CONFIG = {
#     'version': 1,
#     'formatters': [
#         'simple': {
#             'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         }
#     ],
#     'handlers': [
#         'console': {
#             'class': logging.StreamHandler
#             'level': DEBUG,
#             'formatter': 'simple',
#             'stream': 'ext://sys.stdout',
#         }
#     ],
#     'loggers':
#     'simpleExample':
#         level: DEBUG
#     handlers: [console]
#     propagate: no
# root:
#   level: DEBUG
#   handlers: [console]
# }
