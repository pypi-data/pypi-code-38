from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Vat import Vat


class VatMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Vat:
        """
        return Vat(array)