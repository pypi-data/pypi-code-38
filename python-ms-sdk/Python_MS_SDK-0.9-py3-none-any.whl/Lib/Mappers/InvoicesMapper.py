from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Invoice import Invoice


class InvoicesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Invoice:
        """
        return Invoice(array)