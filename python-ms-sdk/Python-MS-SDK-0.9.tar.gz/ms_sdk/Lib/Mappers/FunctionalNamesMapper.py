from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.FunctionalName import FunctionalName


class FunctionalNamesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return FunctionalName:
        """
        return FunctionalName(array)
