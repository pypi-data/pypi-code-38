import logging

import zmq

from om.message import Message


class RPC(object):
    def __init__(self, config, context=None):
        context = context or zmq.Context()
        self.name = config.NAME
        self.sub = context.socket(zmq.SUB)
        self.sub.connect("tcp://{}:{}".format(config.BROKER_HOST, config.BROKER_PUB_PORT))
        self.pub = context.socket(zmq.PUB)
        self.pub.connect("tcp://{}:{}".format(config.BROKER_HOST, config.BROKER_SUB_PORT))
        self.handlers = {}
        self.log = logging.getLogger("rpc")

    def register_handler(self, channel, type, handler):
        """
        :param type: the request type, specify * to catch all types, in this case no other
                     handler will be run for the channel except for the wildcard handler
        :param handler: request handler of the form (request:dict, meta:dict) -> any
                        if the handler returns a dict which contains the key "status",
                        then the value of "status" will be used as the rpc response status.
                        There are no other reserved keys except "status".
        """
        channel = self._ascii(channel)
        type = self._ascii(type)
        self.log.debug("register handler {}:{} -> {}".format(channel, type, handler))
        self.sub.subscribe(b"rpc-req-{}".format(channel))
        self.handlers[(channel, type)] = handler

    def _channel_from_topic(self, topic):
        return topic.split(b"-", 2)[-1]

    def _ascii(self, x):
        if hasattr(x, "encode"):
            return x.encode("ascii")
        else:
            return x

    def find_handler(self, channel, type):
        channel = self._ascii(channel)
        type = self._ascii(type)
        return self.handlers.get((channel, b"*")) or self.handlers.get((channel, type))

    def run(self):
        while True:
            topic, message = Message.from_socket(self.sub)
            channel = self._channel_from_topic(topic)
            request = message["request"]
            type = message["type"]
            del message["request"]
            message["channel"] = channel

            self.log.debug("processing request for {}:{} -> {}".format(topic, channel, request))
            handler = self.find_handler(channel, type)
            if handler:
                try:
                    response = handler(request, message)
                except Exception as e:
                    self.log.exception("exception in handler {}:{}".format(channel, type))
                    response = {"status": "handler_error", "exception": str(e)}
            else:
                self.log.warning("no handler found for {}:{}".format(channel, type))
                response = {"status": "unhandled"}

            self.log.debug("response: {}".format(response))
            result = Message(type=type, name=self.name)
            result["rpc_id"] = message["rpc_id"]
            result["response"] = response
            result.to_socket(self.pub, "rpc-rep-{}".format(channel).encode("ascii"))