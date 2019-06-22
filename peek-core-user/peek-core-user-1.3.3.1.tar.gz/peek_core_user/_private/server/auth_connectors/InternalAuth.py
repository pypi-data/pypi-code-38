import logging
from typing import List

from twisted.cred.error import LoginFailed

from peek_core_user._private.server.controller.PasswordUpdateController import \
    PasswordUpdateController
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.storage.InternalUserGroupTuple import InternalUserGroupTuple
from peek_core_user._private.storage.InternalUserPassword import InternalUserPassword
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user.server.UserDbErrors import UserPasswordNotSetException

logger = logging.getLogger(__name__)


class InternalAuth:

    def checkPassBlocking(self, dbSession, userName, password) -> List[str]:

        results = dbSession.query(InternalUserPassword) \
            .join(InternalUserTuple) \
            .filter(InternalUserTuple.userName == userName) \
            .all()

        if not results or not results[0].password:
            raise UserPasswordNotSetException(userName)

        passObj = results[0]
        if passObj.password != PasswordUpdateController.hashPass(password):
            raise LoginFailed("Username or password is incorrect")

        groups = dbSession.query(InternalGroupTuple) \
            .join(InternalUserGroupTuple) \
            .filter(InternalUserGroupTuple.userId == passObj.userId) \
            .all()

        return [g.groupName for g in groups]

