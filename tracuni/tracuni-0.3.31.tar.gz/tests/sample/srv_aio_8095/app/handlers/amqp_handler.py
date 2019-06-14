import asyncio
import hashlib
import hmac
import json
import os
import ssl
import sys
from functools import partial
from uuid import uuid4
from json import JSONDecodeError
from urllib.parse import urlencode

from app.core.handler import BaseHandler
from app.core.helper import json_encode
from app.core.http_client import HttpClient


class AmqpHandler(BaseHandler):
    routes = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_cln: HttpClient = self.app.http_cln
        self.routes = [
            {
                'route_name': self.config['rabbit']['queue_name'],
                'queue_name': self.config['rabbit']['queue_name'],
                'routing_key': self.config['rabbit']['routing_key'],
                'handler': self.receive
            }
        ]

    async def start(self):
        # перезапуск не завершенных задач
        pass

    async def receive(self, channel, body, envelope, properties):
        self.app.log_info('[i] Request: %s' % body)

        try:
            req = json.loads(body.decode())

            self.app.log_info("[i] Received %r" % req)

            if req.get('name') == 'cb':
                self.app.log_info("Result: {}".format(
                    json_encode(req)
                ))
            else:

                cb_type = None
                cb_address = None

                waiting_for = []
                for name, task in req.get('tasks', {}).items():
                    kind = task.get('api_kind')
                    sub_tasks = task.get('tasks', {})
                    if name == "cb":
                        cb_type = kind
                        cb_address = task.get('address', '')
                    else:
                        if task.get('api_kind') == 'http':
                            url = task.get('address')
                            if url:
                                http_res = self.app.http_cln.request(
                                    "POST",
                                    url,
                                    headers={},
                                    body=json.dumps({
                                        "name": name,
                                        "tasks": sub_tasks
                                    }).encode(),
                                )
                                waiting_for.append(http_res)
                        if task.get('api_kind') == 'amqp':
                            amqp_res = self.task(name, task)
                            waiting_for.append(amqp_res)
                        if task.get('api_kind') == 'db':
                            db_res = getattr(self.app.db_tasks,
                                             task.get('address'))(name, task)
                            waiting_for.append(db_res)

                if waiting_for:
                    response = await asyncio.gather(*waiting_for)
                else:
                    response = []
                response = {
                    "name": req.get("name", "unknown"),
                    "ok": True,
                    "tasks": dict(
                        (
                            response_item.get("name", uuid4().hex),
                            dict(
                                (k, v)
                                for k, v in response_item.items()
                                if k != "name"
                            )
                        )
                        for response_item in response
                    ),
                }
                if cb_type == "http":
                    self.app.http_cln.request(
                        "POST",
                        cb_address,
                        headers={},
                        body=json.dumps(response).encode(),
                    )
                if cb_type == "amqp":
                    await self.task("cb", {
                        "address": cb_address,
                        "tasks": response,
                    })

        except JSONDecodeError:
            self.app.log_err("[x] Error decoding task %r" % body.decode())
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    async def async_task_out(self, tid, data):
        url = 'wrong'

        res_http = await self.app.http_cln.request(
            data['method'],
            url,
            body={},
            headers={},
        )

        # noinspection PyPep8
        try:
            res_body = json.loads(res_http['response'])
            check_code_out = data['params_extra'].get('check_code_out', True)
            if check_code_out:
                res_code = int(res_body['code'])
            else:
                res_code = 0
        except:
            res_body = None
            res_code = 1

        self.app.log_info('[i] Task %i Res body %s' % (tid, json.dumps(res_body)))

        # проверка сответсвия http кода списку
        if res_http:
            http_code = res_http.get('http_code')
        else:
            http_code = 111

