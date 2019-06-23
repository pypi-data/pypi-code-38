from collections import namedtuple

import pytz
from datetime import datetime, timedelta

import logging
from copy import copy
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from typing import List
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexFactory import VortexFactory

from peek_plugin_chat._private.PluginNames import chatFilt, chatPluginName
from peek_plugin_chat._private.storage.ChatTuple import ChatTuple
from peek_plugin_chat._private.storage.MessageTuple import MessageTuple
from peek_plugin_inbox.server.InboxApiABC import InboxApiABC, NewTask

logger = logging.getLogger(__name__)

_deliverdPayloadFilt = {
    "key": "active.task.message.delivered"
}
_deliverdPayloadFilt.update(chatFilt)

AddTaskUserTuple = namedtuple('AddTaskUserTuple', ['userId', 'onDeliveredPayload'])


class TaskController:
    def __init__(self, activeTaskPluginApi: InboxApiABC):
        self._inboxPluginApi = activeTaskPluginApi

        assert isinstance(self._inboxPluginApi, InboxApiABC), (
                "Expected instance of ActiveTaskServerApiABC, received %s" % self._inboxPluginApi)

        self._deliveredEndpoint = PayloadEndpoint(
            _deliverdPayloadFilt, self._processTaskDelivered)

    def shutdown(self):
        self._deliveredEndpoint.shutdown()
        self._deliveredEndpoint = None
        self._soapController = None

    @inlineCallbacks
    def _processTaskDelivered(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        payload = yield payloadEnvelope.decodePayloadDefer()
        logger.debug("_processTaskDelivered called")
        try:
            onDeliverPayload: bytes = payload.tuples
            yield VortexFactory.sendVortexMsgLocally(onDeliverPayload)

        except Exception as e:
            logger.exception(e)

    def _makeUniqueId(self, chatId: int, userId: str):
        return "peek_plugin_chat.new_message.%s.%s" % (userId, chatId)

    def _makeTaskTitle(self, message: MessageTuple):
        if message.priority == MessageTuple.PRIORITY_EMERGENCY:
            return "EMERGENCY SOS CHAT MESSAGE FROM %s" % message.fromUserId

        return "You have a new chat message from %s" % message.fromUserId

    def _makeMessagesRoutePath(self, chatTuple: ChatTuple):
        return "/peek_plugin_chat/messages/%s" % chatTuple.id

    def _notifyBy(self, message: MessageTuple):
        if message.priority == MessageTuple.PRIORITY_EMERGENCY:
            return (NewTask.NOTIFY_BY_SMS
                    | NewTask.NOTIFY_BY_DEVICE_SOUND
                    | NewTask.NOTIFY_BY_DEVICE_DIALOG)

        if message.priority == MessageTuple.PRIORITY_NORMAL_STICKY:
            return (NewTask.NOTIFY_BY_DEVICE_SOUND
                    | NewTask.NOTIFY_BY_DEVICE_DIALOG)

        return (NewTask.NOTIFY_BY_DEVICE_SOUND
                | NewTask.NOTIFY_BY_DEVICE_POPUP)

    def _displayPriority(self, message: MessageTuple):
        if message.priority == MessageTuple.PRIORITY_EMERGENCY:
            return NewTask.PRIORITY_DANGER

        return NewTask.PRIORITY_SUCCESS

    def addTask(self, chat: ChatTuple,
                message: MessageTuple,
                toUsers: List[AddTaskUserTuple]):
        reactor.callLater(0, self._addTask, chat, message, toUsers)

    @inlineCallbacks
    def _addTask(self, chat: ChatTuple,
                 message: MessageTuple,
                 toUsers: List[AddTaskUserTuple]):

        try:

            for toUser in toUsers:
                onDeliveredPayloadEnvelope = None
                if toUser.onDeliveredPayload:
                    filt = copy(_deliverdPayloadFilt)
                    filt["chatId"] = chat.id

                    payload = Payload(filt=filt, tuples=toUser.onDeliveredPayload)
                    payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
                    onDeliveredPayloadEnvelope = yield payloadEnvelope.toVortexMsgDefer()

                newTask = NewTask(
                    pluginName=chatPluginName,
                    uniqueId=self._makeUniqueId(chat.id, toUser.userId),
                    userId=toUser.userId,
                    title=self._makeTaskTitle(message),
                    description=message.message,
                    displayAs=NewTask.DISPLAY_AS_MESSAGE,
                    displayPriority=self._displayPriority(message),
                    routePath=self._makeMessagesRoutePath(chat),
                    onDeliveredPayloadEnvelope=onDeliveredPayloadEnvelope,
                    autoDelete=NewTask.AUTO_DELETE_ON_SELECT,
                    overwriteExisting=True,
                    notificationRequiredFlags=self._notifyBy(message),
                    autoDeleteDateTime=datetime.now(pytz.utc) + timedelta(minutes=4*60)
                )

                yield self._inboxPluginApi.addTask(newTask)


        except Exception as e:
            logger.exception(e)

    def removeTask(self, chatId: int, userId: str):
        reactor.callLater(0, self.removeTask, chatId, userId)

    @inlineCallbacks
    def _removeTask(self, chatId: int, userId: str):
        try:
            yield self._inboxPluginApi.removeTask(chatPluginName,
                                                  self._makeUniqueId(chatId, userId))

        except ValueError:
            # This means it didn't exist.
            pass

        except Exception as e:
            logger.exception(e)
