from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.DeliveryProvider import DeliveryProvider


class DeliveryProvidersMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return DeliveryProvider:
        """
        return DeliveryProvider(array)