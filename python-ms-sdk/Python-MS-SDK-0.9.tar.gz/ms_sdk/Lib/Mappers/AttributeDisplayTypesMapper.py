from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.AttributeDisplayType import AttributeDisplayType


class AttributeDisplayTypesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributeDisplayType:
        """
        return AttributeDisplayType(array)
