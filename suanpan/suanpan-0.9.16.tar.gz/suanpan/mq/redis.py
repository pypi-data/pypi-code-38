# coding=utf-8
from __future__ import absolute_import, print_function

import time
import traceback

import redis

from suanpan import utils
from suanpan.log import logger

MQ_DELIVER_KEY = "_suanpan_mq_deliver"


class RedisMQ(object):
    def __init__(
        self,  # pylint: disable=unused-argument
        redisHost="localhost",
        redisPort=6379,
        redisRealtime=False,
        redisKeepalive=True,
        # redisKeepaliveIDLE=120,
        # redisKeepaliveCNT=2,
        # redisKeepaliveINTVL=30,
        redisSocketConnectTimeout=1,
        options=None,
        client=None,
        **kwargs
    ):
        self.options = options or {}
        self.options.update(
            host=redisHost,
            port=redisPort,
            realtime=redisRealtime,
            keepalive=redisKeepalive,
            # keepidle=redisKeepaliveIDLE,
            # keepcnt=redisKeepaliveCNT,
            # keepintvl=redisKeepaliveINTVL,
            socketConnectTimeout=redisSocketConnectTimeout,
        )
        if client and not isinstance(client, redis.Redis):
            raise Exception("Invalid client: {}".format(client))
        self.client = client or redis.Redis(
            host=self.options["host"],
            port=self.options["port"],
            decode_responses=True,
            socket_keepalive=self.options["keepalive"],
            # socket_keepalive_options={
            #     socket.TCP_KEEPIDLE: self.options["keepidle"],
            #     socket.TCP_KEEPCNT: self.options["keepcnt"],
            #     socket.TCP_KEEPINTVL: self.options["keepintvl"],
            # },
            socket_connect_timeout=self.options["socketConnectTimeout"],
        )

    @property
    def connected(self):
        return bool(self.client.connection)

    def _getQueue(self, name):
        try:
            return self.client.xinfo_stream(name)
        except Exception:
            return {}

    def _getQueueGroups(self, name):
        try:
            return self.client.xinfo_groups(name)
        except Exception:
            return []

    def _lenQueue(self, name):
        try:
            return self.client.xlen(name)
        except Exception:
            return 0

    def listQueueNames(self):
        return self.client.keys("mq-*")

    def getQueueInfo(self, name):
        # queue = self._getQueue(name)
        length = self._lenQueue(name)
        groups = self._getQueueGroups(name)
        pending = sum(group.get("pending", 0) for group in groups)
        return {
            "name": name,
            "groups": groups,
            # "length": queue.get("length", 0),
            "length": length,
            "pending": pending,
        }

    def createQueue(self, name, group="default", consumeID="0", force=False, existOk=False):
        logger.debug("Create Queue {}-{}".format(name, group))
        if force:
            self.deleteQueue(name)
        return self._createQueue(name, group=group, consumeID=consumeID, existOk=existOk)

    def _createQueue(self, name, group="default", consumeID="0", existOk=False):
        try:
            return self.client.xgroup_create(name, group, id=consumeID, mkstream=True)
        except Exception:
            traceback.print_exc()
            if not existOk:
                raise Exception("Queue existed: {}".format(name))

    def deleteQueue(self, *names):
        return self.client.delete(*names)

    # def hasQueue(self, name, group="default"):
    #     try:
    #         queue = self.client.xinfo_stream(name)
    #         groups = self.client.xinfo_groups(name)
    #         return any(g["name"].decode() == group for g in groups)
    #     except Exception:
    #         return False

    def sendMessage(
        self, queue, data, messageID="*", maxlen=1000, trimImmediately=False
    ):
        return self.client.xadd(
            queue, data, id=messageID, maxlen=maxlen, approximate=(not trimImmediately)
        )

    def recvMessages(
        self,
        queue,
        group="default",
        consumer="unknown",
        noack=False,
        block=False,
        count=1,
        consumeID=">",
    ):
        block = None if not block else 0 if block is True else block
        messages = self.client.xreadgroup(
            group, consumer, {queue: consumeID}, count=count, block=block, noack=noack
        )
        messages = list(self._parseMessagesGenerator(messages, group))

        lostMessageIDs = [
            message["id"]
            for message in messages
            if message["id"] and not message["data"]
        ]
        if lostMessageIDs:
            self.client.xack(queue, group, *lostMessageIDs)
            logger.warning("Messages have lost: {}".format(lostMessageIDs))

        return [message for message in messages if message["data"]]

    def subscribeQueue(
        self,
        queue,
        group="default",
        consumer="unknown",
        noack=False,
        block=True,
        count=1,
        consumeID=">",
        delay=0,
        errDelay=1,
        errCallback=logger.error,
    ):
        self.createQueue(queue, group=group, existOk=True)
        logger.debug("Subscribing Messages")
        while True:
            try:
                messages = self.recvMessages(
                    queue,
                    group=group,
                    consumer=consumer,
                    noack=noack,
                    block=block,
                    count=count,
                    consumeID=consumeID,
                )
            except Exception as e:
                errCallback(e)
                logger.debug("Error in receiving messages. Wait {}s".format(errDelay))
                time.sleep(errDelay)
                self.createQueue(queue, group=group, existOk=True)
                continue

            if not messages:
                logger.debug("Received no messages. Wait {}s".format(delay))
                time.sleep(delay)
                continue

            for message in messages:
                yield message
                self.client.xack(queue, group, message["id"])

    def recvPendingMessagesInfo(
        self, queue, group="default", consumer="unknown", start="-", end="+", count=None
    ):
        return self.client.xpending_range(
            queue, group, start, end, count, consumername=consumer
        )

    def retryPendingMessages(
        self,
        queue,
        group="default",
        consumer="unknown",
        count=100,
        maxTimes=3,
        timeout=1,
        errCallback=logger.error,
        maxlen=1000,
        trimImmediately=False,
    ):
        logger.debug("Retrying Pending Messages")

        def _getPendingMessages():
            try:
                return self.recvMessages(
                    queue,
                    group=group,
                    consumer=consumer,
                    block=False,
                    count=count,
                    consumeID="0",
                )
            except Exception:
                logger.warning("Error in getting pending messages:")
                logger.warning(traceback.format_exc())
                return []

        pendingMessages = {msg["id"]: msg for msg in _getPendingMessages()}
        if not pendingMessages:
            logger.debug("Nothing to retry!")
            return

        pendingInfos = {
            msg["message_id"]: msg
            for msg in self.recvPendingMessagesInfo(
                queue, group=group, consumer=consumer, count=count
            )
        }

        for mid in pendingMessages.keys():
            message = pendingMessages[mid]
            info = pendingInfos.get(mid, {})
            message = utils.merge(message, info)
            data = message["data"]
            deliveredTimes = int(data.get(MQ_DELIVER_KEY, 1))
            if deliveredTimes >= maxTimes:
                logger.error(
                    "Message {} retry failed {} times. Drop!".format(
                        mid, deliveredTimes
                    )
                )
                errCallback(message)
                self.client.xack(queue, group, message["id"])
                continue
            timeSinceDelivered = message.get("time_since_delivered", 0)
            if timeSinceDelivered < timeout:
                logger.warning(
                    "Message {} maybe lost: {} < {}".format(
                        mid, timeSinceDelivered, timeout
                    )
                )
                continue
            success = self.client.xack(queue, group, message["id"])
            if success:
                data.update({MQ_DELIVER_KEY: deliveredTimes + 1})
                newMID = self.sendMessage(
                    queue, data, maxlen=maxlen, trimImmediately=trimImmediately
                )
                logger.warning(
                    "Message send back to queue: {} -> {}".format(mid, newMID)
                )

    def _parseMessagesGenerator(self, messages, group):
        for message in messages:
            queue, items = message
            for item in items:
                mid, data = item
                yield {"id": mid, "data": data, "queue": queue, "group": group}
