from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.EntityAttributeValue import EntityAttributeValue


class EntityAttributeValuesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return EntityAttributeValue:
        """
        return EntityAttributeValue(array)
