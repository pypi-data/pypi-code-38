from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.AttributeType import AttributeType


class AttributeTypesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Address:
        """
        return AttributeType(array)
