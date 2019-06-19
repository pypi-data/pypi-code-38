from typing import Callable

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLoginResponseTuple import UserLoginResponseTuple
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from peek_core_user.tuples.login.UserLogoutResponseTuple import UserLogoutResponseTuple

UserPostLoginHookCallable = Callable[[UserLoginResponseTuple], Deferred]

UserPostLogoutHookCallable = Callable[[UserLogoutResponseTuple], Deferred]


class UserLoginApiABC(metaclass=ABCMeta):
    @abstractmethod
    def logout(self,
               logoutTuple: UserLogoutAction) -> Deferred:  # [UserLogoutResponseTuple]:
        """ Logout

        :param logoutTuple
        """

    @abstractmethod
    def login(self, loginTuple: UserLoginAction) -> Deferred:  # [UserLoginResponseTuple]:
        """ Login

        :param loginTuple
        """
