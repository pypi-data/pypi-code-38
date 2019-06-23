from typing import Optional, List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_core_user.tuples.UserDetailTuple import UserDetailTuple


class UserInfoApiABC(metaclass=ABCMeta):
    @abstractmethod
    def user(self, userName: str) -> Deferred:
        """ Users

        :param userName: The userName of the user to retrieve

        :return: A Deferred, firing with Optional[UserDetailTuple]
        """

    @abstractmethod
    def userBlocking(self, userName:str, ormSession=None) -> Optional[UserDetailTuple]:
        """ User Details for User ID

        Return an instance of c{UserDetailTuple} for the userName provided.
        :param userName: The username to retrive the details for
        :param ormSession: Specify the ormSession to use, otherwise it may close the
                            current session.

        :return UserDetailTuple
        """

    @abstractmethod
    def users(self, likeTitle: Optional[str] = None,
              groupNames: Optional[List[str]] = None) -> Deferred:
        """ Users

        :param likeTitle: An optional string to look for in the title of the users
        :param groupNames: An optional list of group names to include users for.

        :return: A Deferred, callbacking with a List[UserDetailTuple]
        """

    @abstractmethod
    def groups(self, likeTitle: Optional[str] = None) -> Deferred:
        """ Groups

        :param likeTitle: An optional string to look for in the title of the groups

        :return: A Deferred, callbacking with a List[GroupDetailTuple]
        """

    @abstractmethod
    def peekDeviceTokenForUser(self, userName:str) -> Deferred:  # [Optional[str]]:
        """Peek Device Token for Logged in User

        Return the first peek device token for a device this user is logged in to.
        Otherwise, return None

        :return Peek Device Token or None
        """


    @abstractmethod
    def peekUserForDeviceToken(self, deviceToken) -> Deferred:  #Optional[UserDetailTuple]:
        """Peek User for Device Token

        Return a user detail tuple for a user logged into a device with deviceToken

        :return UserDetail or None
        """