from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.PaymentProvider import PaymentProvider


class PaymentProvidersMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return PaymentProvider:
        """
        return PaymentProvider(array)