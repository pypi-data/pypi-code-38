import logging

from twisted.internet.defer import inlineCallbacks

from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user.tuples.UserListItemTuple import UserListItemTuple
from peek_core_user.tuples.GroupDetailTuple import GroupDetailTuple
from peek_core_user.tuples.UserDetailTuple import UserDetailTuple
from vortex.TupleSelector import TupleSelector

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)

from peek_core_user._private.worker.tasks.UserImportInternalUserTask import \
    importInternalUsers

from peek_core_user._private.worker.tasks.UserImportInternalGroupTask import \
    importInternalGroups


class ImportController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    def setTupleObserver(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    @inlineCallbacks
    def importInternalUsers(self, importHash:str, usersVortexMsg: bytes):
        #: result: InternalUserImportResultTuple
        result = yield importInternalUsers.delay(importHash, usersVortexMsg)

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(InternalUserTuple.tupleName(), {})
        )

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(UserDetailTuple.tupleName(), {})
        )

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(UserListItemTuple.tupleName(), {})
        )

        return result

    @inlineCallbacks
    def importInternalGroups(self, importHash:str, groupsVortexMsg: bytes):
        #: result: InternalGroupImportResultTuple
        result = yield importInternalGroups.delay(importHash, groupsVortexMsg)

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(InternalGroupTuple.tupleName(), {})
        )

        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(GroupDetailTuple.tupleName(), {})
        )

        return result
