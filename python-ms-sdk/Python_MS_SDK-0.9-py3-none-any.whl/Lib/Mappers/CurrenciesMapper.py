from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Currency import Currency


class CurrenciesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Currency:
        """
        return Currency(array)