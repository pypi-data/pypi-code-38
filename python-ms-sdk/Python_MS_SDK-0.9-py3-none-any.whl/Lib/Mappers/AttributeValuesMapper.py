from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.AttributeValue import AttributeValue


class AttributeValuesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributeValue:
        """
        return AttributeValue(array)
