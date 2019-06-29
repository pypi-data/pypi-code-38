import logging
from datetime import datetime, timedelta
from typing import List

import pytz
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall

from peek_plugin_chat._private.storage.ChatTuple import ChatTuple
from peek_plugin_chat._private.storage.ChatUserTuple import ChatUserTuple
from peek_plugin_chat._private.storage.MessageReadPayloadTuple import \
    MessageReadPayloadTuple
from peek_plugin_chat._private.storage.MessageTuple import MessageTuple
from peek_plugin_chat._private.tuples.ChatUserReadActionTuple import \
    ChatUserReadActionTuple
from peek_plugin_chat._private.tuples.CreateChatActionTuple import CreateChatActionTuple
from peek_plugin_chat._private.tuples.SendMessageActionTuple import SendMessageActionTuple
from peek_plugin_chat.server.ChatApiABC import NewMessage
from peek_core_user.server.UserApiABC import UserApiABC
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.VortexFactory import VortexFactory
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .TaskController import TaskController, AddTaskUserTuple

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    PROCESS_PERIOD = 600.0  # 10 minutes

    def __init__(self, dbSessionCreator,
                 ourApi,  #: ChatApi,
                 userPluginApi: UserApiABC,
                 taskController: TaskController,
                 tupleObservable: TupleDataObservableHandler):

        self._ourApi = ourApi
        self._ormSessionCreator = dbSessionCreator
        self._userPluginApi = userPluginApi
        self._taskController = taskController
        self._tupleObserver = tupleObservable

        self._processLoopingCall = LoopingCall(self._deleteOnDateTime)

    def start(self):
        d = self._processLoopingCall.start(self.PROCESS_PERIOD, now=False)
        d.addErrback(vortexLogFailure, logger)
        return self

    def shutdown(self):
        self._processLoopingCall.stop()

    def _notifyOfChatListUpdate(self, userId: str) -> None:
        """ Notify of Chat List Update

        Notify the observer of the data it needs to emit to the users.

        :param userId: The user to notify of all chat updates

        """

        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(ChatTuple.tupleType(), {"userId": userId})
        )

    def _notifyOfChatUpdate(self, chatId: int) -> None:
        """ Notify of Chat Update

        Notify the observer of the data it needs to emit to the users.

        :param chatId: The id of the chat that has been updated.

        """

        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(ChatTuple.tupleType(), {"chatId": chatId})
        )

    def processTupleAction(self, tupleAction: TupleActionABC):
        if isinstance(tupleAction, CreateChatActionTuple):
            return self._processCreateChatAction(tupleAction)

        if isinstance(tupleAction, SendMessageActionTuple):
            return self._processSendMessageAction(tupleAction)

        if isinstance(tupleAction, ChatUserReadActionTuple):
            return self._processChatReadAction(tupleAction)

        raise Exception("Unhandled tuple action %s" % tupleAction.tupleType())

    @deferToThreadWrapWithLogger(logger)
    def externalMessageQueued(self, toUserId: str):
        """ External Message Sent
        
        This method is used to notify the main controller when a new message has
        been queued from an external system.
        """

    @deferToThreadWrapWithLogger(logger)
    def _processCreateChatAction(self, action: CreateChatActionTuple):
        """ Process Create Chat action by user

        Process updates to the task from the UI.

        """
        session = self._ormSessionCreator()
        allUserIds = action.userIds + [action.fromUserId]

        try:
            self._getOrCreateChatBlocking(allUserIds, [], session)

        finally:
            session.close()

        for userId in allUserIds:
            self._notifyOfChatListUpdate(userId)

    def _getOrCreateChatBlocking(self, allUserIds: List[str],
                                 extUserIds: List[str],
                                 session) -> ChatTuple:
        extUserIds = set(extUserIds)
        usersKey = ','.join(sorted(allUserIds))

        # Check if there is an existing chat
        chatTuple = (session
                     .query(ChatTuple)
                     .filter(ChatTuple.usersKey == usersKey)
                     .all())
        # Convert from the array
        chatTuple = chatTuple[0] if chatTuple else None
        if chatTuple:  # There is an existing one.
            # Bump the chat to the top.
            chatTuple.lastActivity = datetime.now(pytz.utc)

        else:
            # Create the new chat tuple
            chatTuple = ChatTuple()
            chatTuple.lastActivity = datetime.now(pytz.utc)
            chatTuple.usersKey = usersKey
            session.add(chatTuple)

            for userId in allUserIds:
                chatUserTuple = ChatUserTuple()
                chatUserTuple.userId = userId
                chatUserTuple.lastReadDate = datetime.now(pytz.utc)
                chatUserTuple.isUserExternal = userId in extUserIds
                chatUserTuple.userName = userId

                chatTuple.users.append(chatUserTuple)
                session.add(chatUserTuple)
        session.commit()

        return chatTuple

    # -------------------------------------------------------------------------
    # Process send Message Actions
    @inlineCallbacks
    def _processSendMessageAction(self, action: SendMessageActionTuple):
        """ Process Task Update

        Process updates to the task from the UI.

        """
        chatTuple, messageTuple = yield self._processSendMessageActionInThread(action)

        # Tell the API that we've received a message, let it notify who it needs
        self._ourApi.notifyOfReceivedMessage(chatTuple, messageTuple)

        # Get the IDs needed for the updates
        users = [chatUser for chatUser in chatTuple.users
                 if not chatUser.isUserExternal]
        chatId = chatTuple.id

        # Send alerts to the other users.
        alertUsers = [AddTaskUserTuple(userId=u.userId, onDeliveredPayload=None)
                      for u in users if u.userId != action.fromUserId]
        yield self._taskController.addTask(chatTuple, messageTuple, alertUsers)

        for user in users:
            self._notifyOfChatListUpdate(user.userId)

        self._notifyOfChatUpdate(chatId)

    @deferToThreadWrapWithLogger(logger)
    def _processSendMessageActionInThread(self, action: SendMessageActionTuple):
        """ Process Task Update
        
        Process updates to the task from the UI.
        
        """
        session = self._ormSessionCreator()

        try:
            chatTuple = (session
                         .query(ChatTuple)
                         .filter(ChatTuple.id == action.chatId)
                         .one())

            # Get the chat user for this user, sending a message implies they
            # have read up to date.
            chatUserTuple = list(filter(lambda cu: cu.userId == action.fromUserId,
                                        chatTuple.users))[0]

            # Create the new chat tuple
            messageTuple = MessageTuple()
            messageTuple.chatId = chatTuple.id
            messageTuple.fromUserId = action.fromUserId
            messageTuple.message = action.message
            messageTuple.priority = action.priority
            messageTuple.dateTime = datetime.now(pytz.utc)
            session.add(messageTuple)

            # Update the last activity and lastReadDate for the sender
            chatTuple.lastActivity = datetime.now(pytz.utc)
            chatUserTuple.lastReadDate = datetime.now(pytz.utc)

            # Commit the changes.
            session.commit()
            session.refresh(chatTuple)
            session.refresh(messageTuple)
            session.expunge_all()

            return chatTuple, messageTuple


        finally:
            session.close()

    # -------------------------------------------------------------------------
    # Process Chat Read Actions

    @inlineCallbacks
    def _processChatReadAction(self, action: ChatUserReadActionTuple):
        """ Process Create Chat Read action

        Updates the last read date for the user, sends any waiting payloads fo those
        messages

        """
        chatId, userId = yield self._processChatReadActionInThread(action)

        # Remove the unread message if there are any
        yield self._taskController.removeTask(chatId, userId)

    @deferToThreadWrapWithLogger(logger)
    def _processChatReadActionInThread(self, action: ChatUserReadActionTuple):
        """ Process Create Chat Read action

        Updates the last read date for the user, sends any waiting payloads fo those
        messages

        """
        session = self._ormSessionCreator()

        try:
            # Find the chat user and update the last read date.
            chatUser = (session
                        .query(ChatUserTuple)
                        .filter(ChatUserTuple.id == action.chatUserId)
                        .one())

            chatId = chatUser.chatId
            userId = chatUser.userId

            chatUser.lastReadDate = action.readDateTime

            # Send any onRead payloads that are required, and cleanup.
            msgPayloads = (session
                           .query(MessageReadPayloadTuple)
                           .join(MessageTuple,
                                 MessageTuple.id == MessageReadPayloadTuple.messageId)
                           .filter(MessageTuple.dateTime <= action.readDateTime)
                           .filter(MessageReadPayloadTuple.chatUserId == chatUser.id)
                           .all())

            for msgPayload in msgPayloads:
                if msgPayload.onReadPayload:
                    reactor.callLater(
                        0, VortexFactory.sendVortexMsgLocally, msgPayload.onReadPayload
                    )

                session.delete(msgPayload)

            session.commit()

            return chatId, userId

        finally:
            session.close()

    # -------------------------------------------------------------------------
    # Send Message From External User

    @inlineCallbacks
    def sendMessageFromExternalUser(self, newMessage: NewMessage):
        """ Send Message From External User
        
        This method handles the messages sent via the API
        
        :param newMessage: A new message to send, in the APIs simple format.
        :return: None
        
        """
        chatTuple, messageTuple, allUserIds = (
            yield self._sendMessageFromExternalUserInThread(newMessage)
        )

        # Send alerts to the other users.
        toUsers = [AddTaskUserTuple(userId=u.toUserId,
                                    onDeliveredPayload=u.onDeliveredPayload)
                   for u in newMessage.toUsers]
        self._taskController.addTask(chatTuple, messageTuple, toUsers)

        for userId in allUserIds:
            self._notifyOfChatListUpdate(userId)

        self._notifyOfChatUpdate(chatTuple.id)

    @deferToThreadWrapWithLogger(logger)
    def _sendMessageFromExternalUserInThread(self, newMessage: NewMessage):
        """ Send Message From External User

        This method handles the messages sent via the API

        :param newMessage: A new message to send, in the APIs simple format.
        :return: None

        """

        session = self._ormSessionCreator()
        try:
            # Create an array of all users in the chat
            allUserIds = [nmu.toUserId for nmu in newMessage.toUsers]
            allUserIds += [newMessage.fromExtUserId]

            # Get or create the chat tuple
            chatTuple = self._getOrCreateChatBlocking(
                allUserIds, [newMessage.fromExtUserId], session
            )

            # Ensure that the external user is set as an external user
            extChatUser = list(filter(lambda cu: cu.userId == newMessage.fromExtUserId,
                                      chatTuple.users))[0]
            extChatUser.isUserExternal = True

            # Create the new chat tuple
            messageTuple = MessageTuple()
            messageTuple.chatId = chatTuple.id
            messageTuple.fromUserId = newMessage.fromExtUserId
            messageTuple.message = newMessage.message
            messageTuple.priority = newMessage.priority
            messageTuple.dateTime = datetime.now(pytz.utc)
            session.add(messageTuple)

            # Create a map of userIds to IDs for the user read payloads
            chatUserByUserId = {cu.userId: cu for cu in chatTuple.users}

            # Create the read payload tuples
            for toUser in newMessage.toUsers:
                if not toUser.onReadPayload:
                    continue

                readPayload = MessageReadPayloadTuple()
                readPayload.message = messageTuple
                readPayload.chatUser = chatUserByUserId[toUser.toUserId]
                readPayload.onReadPayload = toUser.onReadPayload
                session.add(readPayload)

            session.commit()
            session.refresh(chatTuple)
            session.refresh(messageTuple)
            session.expunge_all()

            return chatTuple, messageTuple, allUserIds


        finally:
            session.close()

    # -------------------------------------------------------------------------
    # Create Chat

    @deferToThreadWrapWithLogger(logger)
    def createChat(self, fromExtUserId: str, toUserIds: List[str]) -> None:
        """ Create Chat
        
        Used by the API
        
        """

        session = self._ormSessionCreator()
        try:
            # Create an array of all users in the chat
            allUserIds = list(toUserIds)
            allUserIds += [fromExtUserId]

            # Get or create the chat tuple
            chatTuple = self._getOrCreateChatBlocking(
                allUserIds, [fromExtUserId], session
            )
            chatId = chatTuple.id

            session.commit()

        finally:
            session.close()

        for userId in allUserIds:
            self._notifyOfChatListUpdate(userId)

        self._notifyOfChatUpdate(chatId)

    # -------------------------------------------------------
    # Delete Old Messages
    # -------------------------------------------------------
    @deferToThreadWrapWithLogger(logger)
    def _deleteOnDateTime(self):
        session = self._ormSessionCreator()
        # chatUsersIdsToUpdate = set()

        try:
            expiredMessageDate = datetime.now(pytz.utc) - timedelta(days=2)
            expiredChatDate = datetime.now(pytz.utc) - timedelta(days=5)

            # Query for the chats to delete
            chatUsersIdsToUpdate = set(
                map(lambda i: i[0],
                    session.query(ChatUserTuple.userId)
                    .join(ChatTuple, ChatTuple.id == ChatUserTuple.chatId)
                    .filter(ChatTuple.lastActivity < expiredChatDate)
                    )
            )

            # No updates required for message expiration, just delete them.
            (
                session
                    .query(MessageTuple)
                    .filter(MessageTuple.dateTime < expiredMessageDate)
                    .delete()
            )

            # Delete Chats
            (
                session
                    .query(ChatTuple)
                    .filter(ChatTuple.lastActivity < expiredChatDate)
                    .delete()
            )

            session.commit()

        finally:
            session.close()

        for userId in chatUsersIdsToUpdate:
            self._notifyOfChatListUpdate(userId)
