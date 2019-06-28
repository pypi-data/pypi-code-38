from tornado.websocket import WebSocketHandler
from tornado.web import HTTPError
from tornado import gen
from .authentication import UserMixin
from ..utils import json_utils
import functools
import logging
import uuid

"""
    Implentation of the json rpc 2.0 spec.
"""

LOGGER = logging.getLogger(__name__)


class JsonRpcException(Exception):
    def __init__(self, code, message):
        super().__init__(self, message)
        self.js_code = code
        self.js_message = message


class JsonRpcHandler(UserMixin, WebSocketHandler):
    def initialize(self):
        self.id = str(uuid.uuid4())

    @property
    def manager(self):
        return self.settings["manager"]

    @property
    def procedures(self):
        return self.manager.proc_names

    def open(self):
        user = self.get_current_user()
        if user:
            self.manager.add_client(self)
            LOGGER.info("user: %s", user)
            self.write_message(
                json_utils.dumps({"signal": "set_user", "message": user})
            )
        elif self.settings["debug"] is False:
            raise HTTPError(403)
        else:
            self.manager.add_client(self)

    def get_params(self, content):
        if isinstance(content["params"], dict):
            return [], content["params"]
        elif isinstance(content["params"], list):
            return content["params"], {}
        else:
            raise JsonRpcException(-32602, "Params neither list or dict")

    @gen.coroutine
    def perform(self, content, result):
        method = content["method"]
        if method == "authenticate":
            result["result"] = self.get_transfer_user(content["params"][0])
            self.write_message(json_utils.dumps(result))
        else:
            content["client_id"] = self.id
            content["current_user"] = self.get_current_user()
            future = yield self.manager.put(content)
            if future:
                future.add_done_callback(functools.partial(self.work_done, result))

    @gen.coroutine
    def on_message(self, data):
        content = json_utils.loads(data)
        LOGGER.info(content)
        result = {"jsonrpc": "2.0"}
        try:
            if content.get("jsonrpc") != "2.0":
                raise JsonRpcException(-32600, "protocol not supported")
            ref = content.get("id")
            if ref:
                result["id"] = ref

            method = content.get("method")
            if method is None:
                raise JsonRpcException(-32600, "no method")
            if method[0] == "_":
                raise JsonRpcException(-32600, "method private")
            if method in self.procedures + ["authenticate"]:
                yield self.perform(content, result)
                result = None
            else:
                raise JsonRpcException(-32600, f"no such method: {method}")

            if ref is None:
                result = None  # its a notification

        except JsonRpcException as ex:
            LOGGER.exception(ex)
            result["error"] = {"code": ex.js_code, "message": ex.js_message}
        except Exception as ex:
            LOGGER.exception(ex)
            result["error"] = {"code": -32000, "message": str(ex)}
        finally:
            if result:
                LOGGER.debug(repr(result))
                self.write_message(json_utils.dumps(result))

    def work_done(self, result, future):
        try:
            output = future.result()
            result["result"] = output
        except Exception as ex:
            result["error"] = {"code": -32000, "message": str(ex)}
        self.write_message(json_utils.dumps(result))

    def on_close(self):
        self.manager.remove_client(self)
