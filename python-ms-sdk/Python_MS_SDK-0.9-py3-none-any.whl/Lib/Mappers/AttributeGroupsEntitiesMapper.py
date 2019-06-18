from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.AttributeGroupsEntities import AttributeGroupsEntities


class AttributeGroupsEntitiesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributeGroupsEntities:
        """
        return AttributeGroupsEntities(array)
