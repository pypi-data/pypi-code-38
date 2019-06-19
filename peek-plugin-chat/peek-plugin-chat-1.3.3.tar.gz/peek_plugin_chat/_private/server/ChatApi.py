import logging
from typing import List

from rx.subjects import Subject
from twisted.internet import reactor

from peek_plugin_chat._private.server.controller.MainController import MainController
from peek_plugin_chat._private.storage.ChatTuple import ChatTuple
from peek_plugin_chat._private.storage.MessageTuple import MessageTuple
from peek_plugin_chat.server.ChatApiABC import ChatApiABC, NewMessage, ReceivedMessage
from vortex.DeferUtil import yesMainThread

logger = logging.getLogger(__name__)


class ChatApi(ChatApiABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator
        self._mainController = None

        self._observablesByUserId = {}

    def setMainController(self, mainController: MainController):
        self._mainController = mainController

    def shutdown(self):
        self._mainController = None
        for subject in self._observablesByUserId.values():
            subject.dispose()

    def notifyOfReceivedMessage(self, chat:ChatTuple, message:MessageTuple):
        receivedMessage = ReceivedMessage(
            fromUserId=message.fromUserId,
            allUserIds=[cu.userId for cu in chat.users],
            message=message.message,
            priority=message.priority
        )

        for user in chat.users:
            # checking if it's external only isn't really necessary
            # other APIs could observe any users message.
            if not user.isUserExternal:
                continue

            # We don't notify the sender
            if user.userId == message.fromUserId:
                continue

            # And if no ones watching it, there is nothing to do.
            if user.userId not in self._observablesByUserId:
                continue

            self._observablesByUserId[user.userId].on_next(receivedMessage)

    def sendMessage(self, newMessage: NewMessage) -> None:
        yesMainThread()
        return self._mainController.sendMessageFromExternalUser(newMessage)

    def createChat(self, fromExtUserId: str, toUserIds: List[str]) -> None:
        yesMainThread()
        return self._mainController.createChat(fromExtUserId, toUserIds)

    def receiveMessages(self, toExtUserId: str) -> Subject:
        yesMainThread()
        if toExtUserId not in self._observablesByUserId:
            self._observablesByUserId[toExtUserId] = Subject()
        return self._observablesByUserId[toExtUserId]
