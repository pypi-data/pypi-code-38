import asyncio
import json

from aiohttp import web
from aiohttp.web_request import Request
from uuid import uuid4

from app.core.http_server import BaseHandler
from app.core.helper import json_encode
from app.lib.helper import Helper


class HttpHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_cln = self.app.http_cln
        self.helper = Helper(self.app.config, None)

    async def http_in(self, context_span, request: Request):
        req = await self.helper.check_request(request, 'transfer')
        waiting_for = []
        for name, task in req.get('tasks', {}).items():
            sub_tasks = task.get('tasks', {})
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
                db_res = getattr(self.app.db_tasks, task.get('address'))(
                    name, task)
                waiting_for.append(db_res)

        if waiting_for:
            response = await asyncio.gather(*waiting_for)
        else:
            response = []
        response = [el for el in response if el is not None]
        response = {
            "name": req.get("name", "unknown"),
            "ok": True,
            "cvv": 123,
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

        return web.json_response(response, dumps=json_encode)

    async def callback_in(self, context_span, request: Request):
        req = await self.helper.check_request(request, 'transfer')
        self.app.log_info("Result: {}".format(
            json_encode(req)
        ))

    async def gen_error(self, _, request: Request):
        raise Exception("1")

