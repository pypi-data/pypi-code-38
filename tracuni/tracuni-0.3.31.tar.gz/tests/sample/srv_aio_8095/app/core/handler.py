import asyncio
import json
import logging
from abc import ABCMeta

import aioamqp

from app.core.helper import json_encode


class BaseHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, server):
        self.server = server
        self.loop = None

    @property
    def app(self):
        return self.server.app

    @property
    def config(self):
        return self.server.app.config

    async def task(self, name, task):
        time_waited = 0
        to_wait = 1.5
        while True:
            try:
                transport, protocol = await aioamqp.connect(
                    **self.config['rabbit']
                )
                break
            except (OSError, aioamqp.AmqpClosedConnection) as e:
                to_wait = round(min(30, (to_wait ** 1.5)), 2)
                logging.error(
                    "[x] Failed to connect to tasks RabbitMQ: %s. Waiting %s seconds...", e, to_wait)
                await asyncio.sleep(to_wait)
                time_waited += to_wait
        channel = await protocol.channel()

        sub_tasks = task.get('tasks', {})
        data = {
            "name": name,
            "tasks": sub_tasks,
        }
        res = await channel.publish(
            json_encode(data),
            task.get('address'),
            self.config['rabbit']['routing_key']
        )

        await protocol.close()
        # ensure the socket is closed.
        transport.close()
        logging.info('[i] Task sended')

        return {
            "name": name,
            "ok": True,
            "tasks": sub_tasks,
            "result": {
                "message": "task sent",
            },
        }
