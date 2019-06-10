from typing import Callable

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_core_user.server.UserHookApiABC import UserHookApiABC
from peek_core_user.server.UserImportApiABC import UserImportApiABC
from peek_core_user.server.UserInfoApiABC import UserInfoApiABC
from peek_core_user.server.UserLoginApiABC import UserLoginApiABC
from peek_core_user.tuples.login.UserLoginResponseTuple import UserLoginResponseTuple
from peek_core_user.tuples.login.UserLogoutResponseTuple import UserLogoutResponseTuple

UserPostLoginHookCallable = Callable[[UserLoginResponseTuple], Deferred]

UserPostLogoutHookCallable = Callable[[UserLogoutResponseTuple], Deferred]


class UserApiABC(metaclass=ABCMeta):

    @property
    @abstractmethod
    def loginApi(self) -> UserLoginApiABC:
        """ Login API

        Returns the API class that handles the user logins

        :return A reference to the UserLoginApiABC class
        """

    @property
    @abstractmethod
    def importApi(self) -> UserImportApiABC:
        """ Import API

        Returns the API class that can be used to import the internal user/group objects

        :return A reference to the UserImportApiABC class
        """

    @property
    @abstractmethod
    def hookApi(self) -> UserHookApiABC:
        """ Hook API

        Returns the API class that can be used to attach callbacks and observers to the
        login/logout process

        :return A reference to the UserHookApiABC class
        """

    @property
    @abstractmethod
    def infoApi(self) -> UserInfoApiABC:
        """ Info API

        Returns the API class that provides information about users

        :return A reference to the UserInfoApiABC class
        """
