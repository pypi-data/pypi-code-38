# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import itertools
import time
import traceback
import uuid

from suanpan import arguments as baseargs
from suanpan import asyncio, g, runtime, utils
from suanpan.arguments import Bool, BoolOrInt, Float, Int, String
from suanpan.components import Arguments, Component
from suanpan.dw import dw
from suanpan.interfaces import HasDevMode, HasLogger
from suanpan.interfaces.optional import HasBaseServices
from suanpan.log import logger
from suanpan.mq import mq
from suanpan.mstorage import mstorage
from suanpan.objects import Context
from suanpan.storage import storage
from suanpan.utils import json


class Handler(Component):
    def __call__(self, steamObj, message, *arg, **kwargs):
        return self.run(steamObj, message, *arg, **kwargs)

    def run(self, steamObj, message, *arg, **kwargs):
        self.beforeInit()
        context = self.init(message)
        self.afterInit()
        results = self.runFunc(steamObj, context, *arg, **kwargs)
        self.beforeSave()
        outputs = self.save(context, results)
        self.afterSave()
        return outputs

    def init(self, message):
        restArgs = self.getArgList(message)
        globalArgs, restArgs = self.loadGlobalArguments(restArgs=restArgs)
        self.initBase(globalArgs)
        context = self._getContext(message)
        args, restArgs = self.loadComponentArguments(context, restArgs=restArgs)
        context.update(args=args)
        self.current = context  # pylint: disable=attribute-defined-outside-init
        return self.current

    def beforeInit(self):
        logger.debug("Handler {} starting...".format(self.name))

    def afterSave(self):
        logger.debug("Handler {} done.".format(self.name))

    def initCurrent(self, message):
        self.current = Context.froms(  # pylint: disable=attribute-defined-outside-init
            message=message
        )
        return self.current

    @contextlib.contextmanager
    def context(self, message):
        yield Context.froms(message=message)

    def getArgList(self, message):
        inputArguments = itertools.chain(
            *[
                ["--{}".format(arg.key), message.get("in{}".format(i + 1))]
                for i, arg in enumerate(self.getArguments(include="inputs"))
                if message.get("in{}".format(i + 1)) is not None
            ]
        )
        shortRequestID = self.shortenRequestID(message["id"])
        outputArguments = (
            [
                "--{}".format(arg.key),
                arg.getOutputTmpValue(
                    "studio",
                    g.USER_ID,  # pylint: disable=no-member
                    g.APP_ID,  # pylint: disable=no-member
                    g.NODE_ID,  # pylint: disable=no-member
                    "out{}".format(i + 1),
                    shortRequestID,
                ),
            ]
            for i, arg in enumerate(self.getArguments(include="outputs"))
        )
        outputArguments = itertools.chain(
            *[[key, value] for key, value in outputArguments if value is not None]
        )
        return list(itertools.chain(inputArguments, outputArguments))

    def saveOutputs(self, context, results):
        if results is not None:
            outputs = super(Handler, self).saveOutputs(context, results)
            outputs = self.formatAsOuts(outputs)
            outputs = self.stringifyOuts(outputs)
            return outputs
        return None

    def formatAsOuts(self, results):
        return {
            "out{}".format(i + 1): self.getArgumentValueFromDict(results, arg)
            for i, arg in enumerate(self.getArguments(include="outputs"))
            if self.getArgumentValueFromDict(results, arg) is not None
        }

    def stringifyOuts(self, outs):
        return {k: str(v) for k, v in outs.items()}

    def shortenRequestID(self, requestID):
        return requestID.replace("-", "")


class Stream(HasBaseServices, HasLogger, HasDevMode):

    DEFAULT_LOGGER_MAX_LENGTH = 120
    DEFAULT_MESSAGE = {}
    DEFAULT_STREAM_CALL = "call"
    STREAM_ARGUMENTS = [
        String("stream-user-id", required=True),
        String("stream-app-id", required=True),
        String("stream-node-id", required=True),
        String("stream-node-group", default="default"),
        String("stream-recv-queue", required=True),
        BoolOrInt("stream-recv-queue-block", default=60000),
        Float("stream-recv-queue-delay", default=0),
        Int("stream-recv-queue-max-length", default=1000),
        Bool("stream-recv-queue-trim-immediately", default=False),
        Bool("stream-recv-queue-retry", default=False),
        Int("stream-recv-queue-retry-max-count", default=100),
        Float("stream-recv-queue-retry-timeout", default=1.0),
        Int("stream-recv-queue-retry-max-times", default=3),
        String("stream-send-queue", required=True),
        Int("stream-send-queue-max-length", default=1000),
        Bool("stream-send-queue-trim-immediately", default=False),
    ]

    def __init__(self):
        super(Stream, self).__init__()
        self.beforeInit()
        self.init()
        self.afterInit()

    def init(self):
        restArgs = self.getArgList()
        arguments, restArgs = self.loadGlobalArguments(restArgs=restArgs)
        self.args = Arguments.froms(self.argumentsDict(arguments))
        self.options = self.getOptions(self.args)
        self.globals = self.setGlobals(self.args)
        self.baseServices = self.setBaseServices(self.args)
        self.current = self.initCurrent(self.args)

    def beforeInit(self):
        logger.logDebugInfo()
        logger.debug("Stream {} starting...".format(self.name))

    def afterInit(self):
        pass

    def getGlobalArguments(self, *args, **kwargs):
        arguments = super(Stream, self).getGlobalArguments(*args, **kwargs)
        return arguments + self.STREAM_ARGUMENTS

    def generateRequestId(self):
        return uuid.uuid4().hex

    def generateMessage(self, **kwargs):
        message = {}
        message.update(self.DEFAULT_MESSAGE, **kwargs)
        message.setdefault("type", self.DEFAULT_STREAM_CALL)
        message["id"] = self.generateRequestId()
        return message

    def formatMessage(self, message, msg, costTime=None):
        msgs = [message["id"], message.get("type", self.DEFAULT_STREAM_CALL), msg]
        if costTime is not None:
            msgs.insert(-1, "{}s".format(costTime))
        return " - ".join(msgs)

    def streamCall(self, message, *args, **kwargs):
        logger.info(self.formatMessage(message, msg="Start"))
        startTime = time.time()
        try:
            self.current.handler = self.getHandler(message)
            outputs = self.current.handler(self, message, *args, **kwargs) or {}
            endTime = time.time()
            costTime = round(endTime - startTime, 3)
            logger.info(self.formatMessage(message, msg="Done", costTime=costTime))
            if outputs:
                self.sendSuccessMessage(message, outputs)
        except Exception:
            tracebackInfo = traceback.format_exc()
            endTime = time.time()
            costTime = round(endTime - startTime, 3)
            logger.error(
                self.formatMessage(message, msg=tracebackInfo, costTime=costTime)
            )
            self.sendFailureMessage(message, tracebackInfo)

    def handlerCallback(self, *args, **kwargs):
        return self.streamCall(self.generateMessage(), *args, **kwargs)

    def getHandler(self, message):
        streamCall = message.get("type", self.DEFAULT_STREAM_CALL)
        handler = getattr(self, streamCall, None)
        if not handler or not isinstance(handler, Handler):
            raise Exception(
                "Unknown stream handler: {}.{}".format(self.name, streamCall)
            )
        if getattr(handler, "current", None) is None:
            handler.initCurrent(message)
        return handler

    @Handler.use
    def call(self, context, *args):
        raise NotImplementedError("Method not implemented!")

    def beforeCall(self):
        pass

    def afterCall(self):
        pass

    def startCallLoop(self):
        if self.options["recvQueueRetry"]:
            self.retryPendingMessages()
        for message in self.subscribe():
            self.current.message = message["data"]
            self.beforeCall()
            self.streamCall(self.current.message)
            self.afterCall()

    def start(self):
        self.startCallLoop()

    @runtime.globalrun
    def run(self):
        self.start()

    def setDefaultMessageType(self, message):
        message["data"].setdefault("type", self.DEFAULT_STREAM_CALL)
        return message

    def getMessageExtraData(self, message):
        extra = message["data"].get("extra")
        extra = json.loads(extra) if extra else {}
        message["data"].update(extra=extra)
        return message

    def getOptions(self, args):
        return self.defaultArgumentsFormat(args, self.STREAM_ARGUMENTS)

    def initCurrent(self, args):  # pylint: disable=unused-argument
        message = self.generateMessage()
        handler = self.getHandler(message)
        return Context.froms(message=message, handler=handler)

    def setGlobals(self, args):
        g.USER_ID = args.stream_user_id
        g.APP_ID = args.stream_app_id
        g.NODE_ID = args.stream_node_id
        g.NODE_GROUP = args.stream_node_group
        return g

    def createQueues(self, force=False):
        mq.createQueue(self.options["recvQueue"], force=force)
        mq.createQueue(self.options["sendQueue"], force=force)

    def subscribe(self, **kwargs):
        for message in mq.subscribeQueue(
            self.options["recvQueue"],
            group=self.options["nodeGroup"],
            consumer=self.options["nodeId"],
            block=self.options["recvQueueBlock"],
            delay=self.options["recvQueueDelay"],
            **kwargs
        ):
            message = self.setDefaultMessageType(message)
            message = self.getMessageExtraData(message)
            yield message

    def recv(self, **kwargs):
        return mq.recvMessages(
            self.options["recvQueue"],
            group=self.options["nodeId"],
            consumer=self.name,
            **kwargs
        )

    def _send(self, message, data, queue=None, extra=None):
        queue = queue or self.options["sendQueue"]
        message.setdefault("extra", {})
        message["extra"].update(extra or {})
        data = {
            "node_id": self.options["nodeId"],
            "request_id": message["id"],
            "type": message.get("type", self.DEFAULT_STREAM_CALL),
            "extra": json.dumps(message["extra"]),
            **data,
        }
        logger.debug(
            utils.shorten(
                "Send to `{}`: {}".format(queue, data), self.DEFAULT_LOGGER_MAX_LENGTH
            )
        )
        return mq.sendMessage(
            queue,
            data,
            maxlen=self.options["sendQueueMaxLength"],
            trimImmediately=self.options["sendQueueTrimImmediately"],
        )

    def sendSuccessMessage(self, message, data, queue=None, extra=None):
        keys = ["out{}".format(i + 1) for i in range(5)]
        if not self.keysAllIn(data.keys(), keys):
            raise Exception("Success Message data only accept keys: {}".format(keys))
        data = {key: data.get(key) for key in keys if data.get(key) is not None}
        data.update(success="true")
        return self._send(message, data, queue=queue, extra=extra)

    def sendFailureMessage(self, message, msg, queue=None, extra=None):
        if not isinstance(msg, str):
            raise Exception("Failure Message msg only accept string")
        data = {"msg": msg, "success": "false"}
        return self._send(message, data, queue=queue, extra=extra)

    def send(self, results, queue=None, message=None, extra=None):
        outputs = self.current.handler.save(self.current.handler.current, results)
        message = message or self.generateMessage(**self.current.message)
        return self.sendSuccessMessage(message, outputs, queue=queue, extra=extra)

    def sendError(self, msg, queue=None, message=None, extra=None):
        message = message or self.generateMessage(**self.current.message)
        return self.sendFailureMessage(message, msg, queue=queue, extra=extra)

    def sendMissionMessage(self, message, data, queue=None, extra=None):
        keys = ["in{}".format(i + 1) for i in range(5)]
        if not self.keysAllIn(data.keys(), keys):
            raise Exception("Mission Message data only accept keys: {}".format(keys))
        return self._send(message, data, queue=queue, extra=extra)

    def retryPendingMessages(self, **kwargs):
        return mq.retryPendingMessages(
            self.options["recvQueue"],
            group=self.options["nodeGroup"],
            consumer=self.options["nodeId"],
            count=self.options["recvQueueRetryMaxCount"],
            maxTimes=self.options["recvQueueRetryMaxTimes"],
            timeout=self.options["recvQueueRetryTimeout"],
            maxlen=self.options["recvQueueMaxLength"],
            trimImmediately=self.options["recvQueueTrimImmediately"],
            **kwargs
        )

    def keysAllIn(self, keys, kset):
        return len(set(keys) - set(kset)) == 0


class Trigger(Stream):
    INTERVAL = 0
    TRIGGER_ARGUMENTS = [Float("triggerInterval", default=0)]
    DEFAULT_TRIGGER_CALL = "trigger"

    def getGlobalArguments(self, *args, **kwargs):
        arguments = super(Trigger, self).getGlobalArguments(*args, **kwargs)
        return arguments + self.TRIGGER_ARGUMENTS

    def _list(self, data):
        if isinstance(data, (tuple, list)):
            return data
        if data is None:
            return []
        return [data]

    @property
    def interval(self):
        _interval = getattr(self, "_interval", None)
        if _interval is not None:
            return _interval
        return self.args.triggerInterval or self.INTERVAL

    @interval.setter
    def interval(self, value):
        if not isinstance(value, (int, float)):
            raise Exception("Interval must be int or float")
        setattr(self, "_interval", value)

    @Handler.use
    def trigger(self, context, *args):
        raise NotImplementedError("Method not implemented!")

    def beforeTrigger(self):
        pass

    def afterTrigger(self):
        pass

    def loop(self):
        while True:
            yield
            time.sleep(self.interval)

    def triggerCall(self, *args, **kwarags):
        return self.streamCall(
            self.generateMessage(type=self.DEFAULT_TRIGGER_CALL), *args, **kwarags
        )

    def startTriggerLoop(self):
        for data in self.loop():
            self.beforeTrigger()
            self.triggerCall(*self._list(data))
            self.afterTrigger()

    def start(self):
        self.createQueues(force=True)
        asyncio.run([self.startCallLoop, self.startTriggerLoop], thread=True, wait=True)
