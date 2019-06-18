from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.CurrencyRate import CurrencyRate


class CurrenciesRateMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return CurrencyRate:
        """
        return CurrencyRate(array)