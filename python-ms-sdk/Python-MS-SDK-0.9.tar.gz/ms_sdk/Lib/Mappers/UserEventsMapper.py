from ms_sdk.Entities.UserEvent import UserEvent
from ms_sdk.Lib.Mappers.Mapper import Mapper


class UserEventsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return User:
        """
        return UserEvent(array)
