from ms_sdk.Entities.Trigger import Trigger
from ms_sdk.Lib.Mappers.Mapper import Mapper


class TriggersMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return User:
        """
        return Trigger(array)
