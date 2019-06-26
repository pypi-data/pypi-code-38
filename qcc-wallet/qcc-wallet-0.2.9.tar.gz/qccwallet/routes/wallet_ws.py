# coding=utf-8

import config
from ..ws_handler.dispatcher import Dispatcher

base = '{}/{}/wallet/ws'.format(config.VER, config.PLATFORM)
routes = [
    (r'/%s' % base, Dispatcher)
]
