from ms_sdk.Entities.Event import Event
from ms_sdk.Lib.Mappers.Mapper import Mapper


class EventsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return User:
        """
        return Event(array)
