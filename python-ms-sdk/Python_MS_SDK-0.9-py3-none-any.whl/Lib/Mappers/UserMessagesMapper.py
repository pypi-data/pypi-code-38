from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Message import Message


class UserMessagesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Message:
        """
        return Message(array)