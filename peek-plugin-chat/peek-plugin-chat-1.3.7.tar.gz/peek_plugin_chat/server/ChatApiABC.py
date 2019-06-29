from typing import Optional, List

from abc import ABCMeta, abstractmethod
from rx.subjects import Subject


class NewMessageUser:
    """ New Message User
    
    This class represents a user that the message will be sent to.
    
    """

    def __init__(self, toUserId: str,
                 onReadPayload: Optional[bytes] = None,
                 onDeliveredPayload: Optional[bytes] = None):
        """ 
        :param toUserId: The peek userId that matches a user in peek_core_user plugin.

        :param onReadPayload: (Optional) The payload that will be delivered locally
            on Peek Server when the user has read the message.

        """
        # To User
        self.toUserId = toUserId
        if not toUserId:
            raise Exception("toUserId is not optional")

        # On Read Payload
        self.onReadPayload = onReadPayload

        #: On Delivered Payload
        self.onDeliveredPayload = onDeliveredPayload


class NewMessage:
    """ New Message

    This class represents a new message that another plugin can send to a user.

    """

    # Message priorities

    #:  Emergency priority for message
    PRIORITY_EMERGENCY = 1

    #:  Normal priority for a message, the alert will be fleeting
    PRIORITY_NORMAL_FLEETING = 2

    #:  Normal priority for message, the alert will be sticky
    PRIORITY_NORMAL_STICKY = 3

    def __init__(self,
                 fromExtUserId: str,
                 fromExtUserName: str,
                 toUsers: List[NewMessageUser],
                 message: str,
                 priority: int = PRIORITY_NORMAL_FLEETING,
                 ):
        """ 
        :param fromExtUserId: The external user id of the user sending the message.
            This doesn't have to match a userId in the peek_core_user plugin.
    
        :param fromExtUserName: The name of the external user (or system) sending the
            message.
    
        :param toUsers: A list of users to send the message to.
        
        :param message: The message to send to the user.
        
        :param priority: The priority of this message, some messages may be emergency 
            messages.
        
        """
        # From User
        self.fromExtUserId = self._required(fromExtUserId, "fromExtUserId")
        self.fromExtUserName = self._required(fromExtUserName, "fromExtUserName")

        # To User
        self.toUsers = self._required(toUsers, "toUsers")

        # Message
        self.message = self._required(message, "message")
        self.priority = self._required(priority, "priority")

    def _required(self, val, desc):
        if not val:
            raise Exception("%s is not optional" % desc)

        return val


class ReceivedMessage:
    """ Received Message

    This class represents a message sent from a peek user to an external system.

    """

    # Message priorities
    PRIORITY_EMERGENCY = NewMessage.PRIORITY_EMERGENCY
    PRIORITY_NORMAL_FLEETING = NewMessage.PRIORITY_NORMAL_FLEETING
    PRIORITY_NORMAL_STICKY = NewMessage.PRIORITY_NORMAL_STICKY

    def __init__(self,
                 fromUserId: str,
                 allUserIds: List[str],
                 message: str,
                 priority: int
                 ):
        """
        :param fromUserId: The peek userId sending the message.

        :param allUserIds: All the userIds in this chat.

        :param message: The message sent by the peek user.

        :param priority: The priority of this message sent.

        """
        # From User
        self.fromUserId = fromUserId

        # All Users
        self.allUserIds = allUserIds

        # Message
        self.message = message
        self.priority = priority

    def _required(self, val, desc):
        if not val:
            raise Exception("%s is not optional" % desc)

        return val


class ChatApiABC(metaclass=ABCMeta):
    @abstractmethod
    def sendMessage(self, newMessage: NewMessage) -> None:
        """ Send a Message

        Send a new chat message to a user.
        
        :param newMessage: The definition of the message to send.
        
        """

    @abstractmethod
    def createChat(self, fromExtUserId: str, toUserIds: List[str]) -> None:
        """ Create a Chat

        Send a new chat message to a user.

        :param fromExtUserId: The external userId sending the message
        :param toUserIds: The Peek userIds to send the message to

        """

    @abstractmethod
    def receiveMessages(self, toExtUserId: str) -> Subject:
        """ Receive Messages
        
        Get the observable that will be fired when new messages are received.

        It will be fired with C{ReceivedMessage}
        
        :param toExtUserId: The external systems userId, that the plugin wants to
            observe messages for. This is just identifier unique to the external
            system.
            
        :return: A RxJS Observable that will notify observers when a message arrives
            for that external system.
        
        """
