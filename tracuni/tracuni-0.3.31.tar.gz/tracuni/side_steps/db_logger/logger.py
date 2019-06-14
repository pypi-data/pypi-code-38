import json
import asyncio
import logging
from datetime import datetime

import pytz
import aioamqp

from tracuni.misc.helper import dict_from_json
from tracuni.schema.pipe_methods import pipe_mask_secret_catch_essentials


TIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"


class Logger(object):
    def __init__(self):
        self.config = json.load(open('config/main.json', encoding='utf8'))

    def __call__(self, func):
        async def wrapper(that, *args, **kwargs):
            stamp_begin = datetime.now(pytz.utc).strftime(TIME_FORMAT)
            data = await func(that, *args, **kwargs)
            stamp_end = datetime.now(pytz.utc).strftime(TIME_FORMAT)
            body = kwargs.get('body')
            if body:
                body = dict_from_json(body)
            else:
                body = args[0]
            response = kwargs.get('response')
            if response:
                response = dict_from_json(response)
            else:
                response = {}
            if data:
                log_data = {
                    'stamp_begin': stamp_begin,
                    'stamp_end': stamp_end,
                    'func_name': func.__name__,
                    'url': args[-1],
                    'request_headers': kwargs.get('headers', {}),
                    'request': body,
                    'response_headers': data.get('response_headers', {}),
                    'response': response,
                    'service_name': self.config['logging'].get(
                        'service_name',
                        self.config['logging'].get('tracer_svc_name', '')
                    ),
                    'external_key': data.get('external_key', '<unknown>'),
                    'http_code': data.get('http_code', 200)
                }
                await self.log(log_data)
            return data
        return wrapper

    async def log(self, log_data):
        # Connecting to rabbit_mq
        time_waited = 0
        to_wait = 1.5
        while True:
            try:
                transport, protocol = await aioamqp.connect(
                    **self.config['logging']
                )
                break
            except (OSError, aioamqp.AmqpClosedConnection) as e:
                to_wait = round(min(30, (to_wait ** 1.5)), 2)
                logging.info(
                    "[x] Failed to connect to RabbitMQ: "
                    "%s. Waiting %s seconds...",
                    e,
                    to_wait
                )
                await asyncio.sleep(to_wait)
                time_waited += to_wait

        channel = await protocol.channel()
        await channel.publish(
            pipe_mask_secret_catch_essentials(json.dumps(log_data))[0],
            self.config['logging']['exchange_name'],
            self.config['logging']['routing_key']
        )
        await protocol.close()
        # ensure the socket is closed.
        transport.close()
        logging.info('[x] Log sent')
