from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Address import Address


class AddressesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Address:
        """
        return Address(array)
