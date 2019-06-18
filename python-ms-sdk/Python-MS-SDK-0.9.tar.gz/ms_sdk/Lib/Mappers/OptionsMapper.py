from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Option import Option


class OptionsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Option:
        """
        return Option(array)
