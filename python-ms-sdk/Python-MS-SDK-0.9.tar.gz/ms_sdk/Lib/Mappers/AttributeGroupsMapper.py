from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.AttributeGroup import AttributeGroup


class AttributeGroupsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributeGroup:
        """
        return AttributeGroup(array)
