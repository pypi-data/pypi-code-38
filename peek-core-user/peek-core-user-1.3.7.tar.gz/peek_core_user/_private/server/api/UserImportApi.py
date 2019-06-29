import logging

from twisted.internet.defer import Deferred

from peek_core_user._private.server.controller.ImportController import \
    ImportController
from peek_core_user.server.UserImportApiABC import UserImportApiABC

logger = logging.getLogger(__name__)


class UserImportApi(UserImportApiABC):
    def __init__(self, importController: ImportController):
        self._importController = importController

    def shutdown(self):
        pass

    def importInternalUsers(self, importHash: str, usersEncodedPayload: bytes) -> Deferred:
        return self._importController.importInternalUsers(importHash, usersEncodedPayload)

    def importInternalGroups(self, importHash: str, groupsEncodedPayload: bytes) -> Deferred:
        return self._importController.importInternalGroups(importHash, groupsEncodedPayload)
