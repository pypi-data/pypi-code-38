import json
import socketserver
import threading
from uuid import uuid4
from azureml.dataprep.api.engineapi.api import EngineAPI, get_engine_api


class EngineRequestsChannel:
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            with self.request.makefile() as reader:
                with self.request.makefile('w') as writer:
                    request = json.loads(reader.readline())
                    request_secret = request.get('host_secret')
                    if request_secret is None or request_secret != self.server.host_secret:
                        writer.write(json.dumps({'result': 'error', 'error': 'Unauthorized'}))
                    else:
                        operation = request['operation']
                        callback = self.server.handlers.get(operation)
                        if callback is None:
                            writer.write(json.dumps({'result': 'error', 'error': 'InvalidOperation'}))
                        else:
                            callback(request, writer, self.request)

    def __init__(self, engine_api: EngineAPI):
        self._handlers = {}
        self._server = socketserver.TCPServer(("localhost", 0), EngineRequestsChannel.Handler, False)
        # This is the number of requests we can queue up before rejecting connections. Given the engine
        # will be making a request per concurrent partition, 256 gives us enough headroom to handle
        # machines with up to 256 cores.
        self._server.request_queue_size = 256
        self._server.server_bind()
        self._server.server_activate()
        self._server.handlers = self._handlers
        self._server.host_secret = str(uuid4())
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()
        self.port = self._server.server_address[1]
        engine_api.set_host_secret(self._server.host_secret)
        engine_api.set_host_channel_port(self.port)

    def register_handler(self, message: str, callback):
        self._handlers[message] = callback


_requests_channel = None


def get_requests_channel() -> EngineRequestsChannel:
    global _requests_channel
    engine_api = get_engine_api()
    if not _requests_channel:
        _requests_channel = EngineRequestsChannel(engine_api)

    return _requests_channel
