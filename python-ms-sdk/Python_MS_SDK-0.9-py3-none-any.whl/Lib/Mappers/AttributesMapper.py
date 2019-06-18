from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Lib.Mappers.AttributeValuesMapper import AttributeValuesMapper
from ms_sdk.Lib.Mappers.AttributeGroupsMapper import AttributeGroupsMapper
from ms_sdk.Entities.Attribute import Attribute


class AttributesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Attribute:
        """
        attribute = Attribute(array)
        attribute.values = []

        try:
            if array.get('attributeValues'):
                mapper = AttributeValuesMapper()

                if array['attributeValues'].get('id'):
                    attribute.values = mapper.createObject(array['attributeValues'])
                else:
                    for item in array.get('attributeValues').items():
                        attribute.values.append(mapper.createObject(item[1]))
        except BaseException:
            pass

        try:
            if array.get('attributeGroups'):
                mapper = AttributeGroupsMapper()
                attribute.group = mapper.createObject(
                    array.get('attributeGroups'))
        except BaseException:
            pass

        return attribute
