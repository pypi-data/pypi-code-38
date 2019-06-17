from tornado import websocket, gen
import json
from ..service import ctrl_wallet


class Dispatcher(websocket.WebSocketHandler):
    def data_received(self, chunk):
        print('data_received')

    def check_origin(self, origin):
        print('check_origin: %s' % origin)
        lang = self.request.headers.get("Origin")
        print('Lang: %s' % lang)
        return True

    def open(self):
        print("WebSocket opened")

    @gen.coroutine
    def on_message(self, message):
        print(message)
        self.write_message(message)
        try:
            req = json.loads(message)

            print(req)

            if 'method' in req:
                method = req['method']
                params = req['params']

                if method == 'get_transaction':
                    ret = yield ctrl_wallet.tx_info(*tuple(params))
                else:
                    ret = 'unknown'

                self.write_message(ret)
            else:
                self.write_message(u'Missing method in request')

        except json.JSONDecodeError:
            self.write_message(u'Not valid JSON message')

    def on_close(self):
        print("WebSocket closed")
