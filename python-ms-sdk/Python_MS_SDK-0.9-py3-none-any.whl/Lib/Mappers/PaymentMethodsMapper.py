from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.PaymentMethod import PaymentMethod


class PaymentMethodsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return PaymentMethod:
        """
        return PaymentMethod(array)