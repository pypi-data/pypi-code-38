import logging

from rx.subjects import Subject
from twisted.internet.defer import inlineCallbacks

from peek_core_user.server.UserApiABC import UserPostLoginHookCallable, \
    UserPostLogoutHookCallable
from peek_core_user.server.UserHookApiABC import UserHookApiABC
from peek_core_user.tuples.login.UserLoginResponseTuple import UserLoginResponseTuple
from peek_core_user.tuples.login.UserLogoutResponseTuple import UserLogoutResponseTuple

logger = logging.getLogger(__name__)


class UserHookApi(UserHookApiABC):
    def __init__(self):

        self._postLoginHooks = []
        self._postLoginSubject = Subject()

        self._postLogoutHooks = []
        self._postLogoutSubject = Subject()

    def shutdown(self):
        pass

    def addPostLoginHook(self, callable: UserPostLoginHookCallable) -> None:
        self._postLoginHooks.append(callable)

    def removePostLoginHook(self, callable: UserPostLoginHookCallable) -> None:
        self._postLoginHooks.remove(callable)

    def postLoginObservable(self) -> Subject:
        return self._postLoginSubject

    def addPostLogoutHook(self, callable: UserPostLogoutHookCallable) -> None:
        self._postLogoutHooks.append(callable)

    def removePostLogoutHook(self, callable: UserPostLogoutHookCallable) -> None:
        self._postLogoutHooks.remove(callable)

    def postLogoffObservable(self) -> Subject:
        return self._postLogoutSubject

    @inlineCallbacks
    def callLogoutHooks(self, response: UserLogoutResponseTuple):
        """
        Returns Deferred[UserLogoutResponseTuple]:
        """

        for callable in self._postLogoutHooks:
            yield callable(response)

        self._postLoginSubject.on_next(response)

    @inlineCallbacks
    def callLoginHooks(self, response: UserLoginResponseTuple):
        """
        Returns Deferred[UserLoginResponseTuple]

        """

        for callable in self._postLoginHooks:
            yield callable(response)

        self._postLoginSubject.on_next(response)
