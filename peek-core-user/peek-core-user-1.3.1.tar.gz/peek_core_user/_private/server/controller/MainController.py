from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_user._private.server.controller.PasswordUpdateController import \
    PasswordUpdateController
from peek_core_user._private.tuples.InternalUserUpdatePasswordAction import \
    InternalUserUpdatePasswordAction
from peek_core_user.server.UserApiABC import UserApiABC
from peek_core_user.tuples.login.UserLoginAction import UserLoginAction
from peek_core_user.tuples.login.UserLogoutAction import UserLogoutAction
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC


class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator,
                 ourApi: UserApiABC):
        self._ourApi = ourApi
        self._passwordUpdateController = PasswordUpdateController(dbSessionCreator)

    def shutdown(self):
        self._ourApi = None

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        if isinstance(tupleAction, UserLoginAction):
            replyTuples = yield self._ourApi.loginApi.login(tupleAction)
            return replyTuples

        if isinstance(tupleAction, UserLogoutAction):
            replyTuples = yield self._ourApi.loginApi.logout(tupleAction)
            return replyTuples

        if isinstance(tupleAction, InternalUserUpdatePasswordAction):
            replyTuples = yield self._passwordUpdateController.processTupleAction(
                tupleAction
            )
            return replyTuples

        raise NotImplementedError(tupleAction.tupleName())
