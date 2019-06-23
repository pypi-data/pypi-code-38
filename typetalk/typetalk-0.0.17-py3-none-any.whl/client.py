# -*- coding: utf-8 -*-

from .http import Route, HTTPClient

import asyncio


class Client:
    def __init__(self, loop=None, token=None, run_async=False, is_bot=False):
        self.http = HTTPClient(
            loop=loop,
            token=token,
            run_async=run_async,
            is_bot=is_bot)

    def post_message(self, topic_id, message):
        r = Route('POST', '/api/v1/topics/{topic_id}', topic_id=topic_id)
        payload = {}

        if message:
            payload['message'] = message
        else:
            # TODO: throw error
            pass

        if self.run_async:
            return self.http.request(r, json=payload)

        self.http.loop = asyncio.get_event_loop()
        return self.http.loop.run_until_complete(
            self.http.request(
                r,
                json=payload
            )
        )
