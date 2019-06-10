from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred


class UserImportApiABC(metaclass=ABCMeta):
    @abstractmethod
    def importInternalUsers(self, importHash: str, usersEncodedPayload: bytes) -> Deferred:
        """ Import Internal Users

        Add, replace and remove users in the internal DB

        :param importHash: A string representing this group of items to import
        :param usersEncodedPayload: A List[ImportInternalUserTuple] to import,
                wrapped in a serialised payload.

        Wrap the disps list with ::

                dispsVortexMsg = Payload(tuples=users).toVortexMsg()

        Calling this method with no tuples will delete all items with this importHash


        :return: A deferred that fires when the users are loaded

        """

    @abstractmethod
    def importInternalGroups(self, importHash: str, groupsEncodedPayload: bytes) -> Deferred:
        """ Import Internal Groups

        Add, replace and remove users in the internal DB

        :param importHash: A string representing this group of items to import
        :param groupsEncodedPayload: A List[ImportInternalGroupTuple] to import,
                wrapped in a serialised payload.

        Wrap the disps list with ::

                dispsVortexMsg = Payload(tuples=groups).toVortexMsg()

        Calling this method with no tuples will delete all items with this importHash


        :return: A deferred that fires when the groups are loaded

        """
