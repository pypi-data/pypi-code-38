# -*- coding: utf-8 -*-

# Standard Imports
import asyncio

# Internal Imports
from .http import Route, HTTPClient


class Client:
    """Base class for User or Bot"""

    def __init__(
        self,
        token=None,
        run_async=False,
        is_bot=False,
    ):

        if run_async:
            loop = asyncio.get_event_loop()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.http = HTTPClient(
            loop=loop,
            token=token,
            run_async=run_async,
            is_bot=is_bot
        )

    def post_message(self, topic_id, message):
        r = Route(
            'POST',
            '/api/v1/topics/{topic_id}'.format(topic_id=topic_id),
        )
        payload = {}

        if message:
            payload['message'] = message
        else:
            # TODO: throw error
            pass

        if self.run_async:
            return self.http.request(r, json=payload)

        return self.http.loop.run_until_complete(
            self.http.request(
                r,
                json=payload
            )
        )
