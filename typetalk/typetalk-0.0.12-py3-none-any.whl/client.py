# -*- coding: utf-8 -*-

from .http import Route, HTTPClient


class Client:
    def __init__(self, token=None):
        self.http = HTTPClient(token=token)

    def post_message(self, topic_id, message):
        r = Route('POST', '/api/v1/topics/{topic_id}', topic_id=topic_id)
        payload = {}

        if message:
            payload['message'] = message
        else:
            # TODO: throw error
            pass

        return self.http.request(r, json=payload)
