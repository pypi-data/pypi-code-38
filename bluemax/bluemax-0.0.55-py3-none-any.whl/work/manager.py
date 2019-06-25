from tornado.options import options
from tornado.queues import Queue
from tornado.concurrent import Future
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from tornado import gen
from ..utils.status import Status
from ..utils import json_utils
from . import perform
import tornado.ioloop
import importlib
import inspect
import functools
import asyncio
import time
import logging

LOGGER = logging.getLogger(__name__)


class Manager:

    _manager_ = None

    def __init__(self, procedures=None, workers=2):
        self.clients = []
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.status = Status(self.ioloop, self.publish_status, timeout=1)
        self.procedures = {}
        self.proc_names = []
        self.reflection = OrderedDict()
        if procedures:
            self.add_targets(procedures)
        self.stateful = {}

        # we're on the main thread
        perform._manager_ = self
        self._manager_ = self
        self._setup_queues_(workers)
        tornado.ioloop.PeriodicCallback(self.keep_alive, 30000).start()

    def add_targets(self, procedures):
        names = getattr(
            procedures, "__all__", [p for p in dir(procedures) if p[0] != "_"]
        )
        self.procedures.update({name: getattr(procedures, name) for name in names})
        self.proc_names.extend(names)
        self.reflection.update(self.describe(procedures, names))
        LOGGER.info("avail: %s", self.proc_names)

    def get_target(self, name):
        return self.procedures.get(name)

    def publish_status(self, status):
        self.broadcast("set_status", status)

    def keep_alive(self):
        """ used to ping the client """
        msg = str(time.time()).encode("utf8")
        LOGGER.debug("ping %s", msg)
        for client in self.clients:
            client.ping(msg)

    def register_state(self, obj):
        """
            Keeps a stateful object
        """
        name = str(id(obj))
        self.stateful[name] = obj
        return name

    def deregister_state(self, name: str):
        """
            Deletes a stateful object
        """
        del self.stateful[name]

    def _setup_queues_(self, workers):
        self._e = ThreadPoolExecutor()
        self._q = Queue()
        for _ in range(workers):
            self.ioloop.spawn_callback(self.work, self._q)

    def add_client(self, client):
        self.clients.append(client)
        self.status["clients"] = len(self.clients)
        client.write_message(
            json_utils.dumps({"signal": "set_reflect", "message": self.reflection})
        )

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.status["clients"] = len(self.clients)

    def filter_client(self, client, filter_clients):
        """ Does this client meet these criteria """
        return True

    def _broadcast_(self, signal, message, filter_clients=None):
        data = json_utils.dumps({"signal": signal, "message": message})
        for client in self.clients:
            if self.filter_client(client, filter_clients):
                client.write_message(data)

    def broadcast(self, signal, message, filter_clients=None):
        """
            a thread safe way to broadcast
        """
        self.ioloop.spawn_callback(self._broadcast_, signal, message, filter_clients)

    def status_update(self):
        self.status["q"] = self._q.qsize()

    def get_params(self, content):
        if isinstance(content["params"], dict):
            return [], content["params"]
        elif isinstance(content["params"], list):
            return content["params"], {}
        raise Exception("Params neither list or dict")

    @gen.coroutine
    def put(self, content):
        future = Future()
        yield self._q.put((content, future))
        self.status_update()
        return future

    @gen.coroutine
    def work(self, q):
        while True:
            item = yield q.get()
            content, future = item
            try:
                method = content["method"]
                actor = content.get("current_user")
                args, kwargs = self.get_params(content)
                if ":" in method:
                    mod_name, func_name = method.split(":")
                    procedure = getattr(importlib.import_module(mod_name), func_name)
                else:
                    procedure = self.get_target(method)
                LOGGER.info("work on %s", procedure)
                result = yield perform.perform(actor, procedure, args, kwargs)
                if result and isinstance(result, perform.Context):
                    future.set_result(result.result)
                    for signal, message, filter_clients in result.messages:
                        self.broadcast(signal, message, filter_clients)
                else:
                    future.set_result(result)
            except Exception as ex:
                LOGGER.exception(ex)
                future.set_exception(ex)
            finally:
                q.task_done()
                self.status_update()

    @classmethod
    def _annotation_to_str_(cls, annotation):
        try:
            if annotation is None:
                return None
            if isinstance(annotation, str):
                return annotation
            if issubclass(annotation, object):
                return annotation.__name__
        except:
            # for some reason a Tuple was throwing and exception
            pass
        return str(annotation)

    @classmethod
    def describe(cls, target, labels=None):
        """
            Will dir target and inspect each
            function and return an instance of
            this class for each

            functions starting with '_' are ignored
        """
        result = OrderedDict()
        targets = labels if labels else dir(target)
        for key in filter(lambda x: x[0] != "_", targets):
            f = getattr(target, key)
            if inspect.isfunction(f) or inspect.ismethod(f):
                sig = inspect.signature(f)
                s = OrderedDict(
                    [
                        ("name", key),
                        ("params", [str(p) for p in sig.parameters.values()]),
                        (
                            "returns",
                            cls._annotation_to_str_(sig.return_annotation)
                            if sig.return_annotation is not sig.empty
                            else "",
                        ),
                        ("docs", inspect.getdoc(f)),
                        ("auth", hasattr(f, "auth")),
                    ]
                )
                LOGGER.debug(s)
                result[key] = s
            else:
                LOGGER.debug("not avaiable %r", f)
        return result
