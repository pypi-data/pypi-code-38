from typing import Callable

from abc import ABCMeta, abstractmethod
from rx.subjects import Subject
from twisted.internet.defer import Deferred

from peek_core_user.tuples.login.UserLoginResponseTuple import UserLoginResponseTuple
from peek_core_user.tuples.login.UserLogoutResponseTuple import UserLogoutResponseTuple

UserPostLoginHookCallable = Callable[[UserLoginResponseTuple], Deferred]

UserPostLogoutHookCallable = Callable[[UserLogoutResponseTuple], Deferred]


class UserHookApiABC(metaclass=ABCMeta):
    @abstractmethod
    def postLoginObservable(self) -> Subject:
        """ Get the post login observable

        Subscribers will be called just after the user has authenticated

        """

    @abstractmethod
    def postLogoffObservable(self) -> Subject:
        """ Get the post logoff observable

        Subscribers will be called just after the user has logged off

        """

    @abstractmethod
    def addPostLoginHook(self, callable: UserPostLoginHookCallable) -> None:
        """ Add Post Login Hook

        :param callable: This callable will be called just after the user has
        authenticated
        """

    @abstractmethod
    def removePostLoginHook(self, callable: UserPostLoginHookCallable) -> None:
        """ Remove Post Login Hook

        :param callable: This callable to remove from the hooks
        """

    @abstractmethod
    def addPostLogoutHook(self, callable: UserPostLogoutHookCallable) -> None:
        """ Add Post Logout Hook

        :param callable: This callable will be called just after the user has
        logged out
        """

    @abstractmethod
    def removePostLogoutHook(self, callable: UserPostLogoutHookCallable) -> None:
        """ Remove Post Logout Hook

        :param callable: This callable to remove from the hooks
        """
