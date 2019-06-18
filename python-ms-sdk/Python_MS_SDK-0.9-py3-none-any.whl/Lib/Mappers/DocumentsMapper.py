from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Lib.Mappers.AttributesMapper import AttributesMapper
from ms_sdk.Lib.Mappers.FunctionalNamesMapper import FunctionalNamesMapper
from ms_sdk.Entities.Document import Document


class DocumentsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return Document:
        """
        document = Document(array)

        try:
            if array.get('attributes') and array.get('attributeValues'):
                document.attributes = []
                mapper = AttributesMapper()

                for attribute in array.get('attributes').items():
                    attribute = attribute[1]
                    attribute.update(self.getAttributeValues(attribute, array['attributeValues']))
                    document.attributes.append(mapper.createObject(attribute))
        except:
            pass

        try:
            if array.get('functionalNames'):
                mapper = FunctionalNamesMapper()
                document.functionalName = mapper.createObject(array.get('functionalNames').get(list(array.get('functionalNames'))[0]))
        except:
            pass

        return document

    def getAttributeValues(self, attribute, attributeValues):
        """
        :param attribute:
        :param attributeValues:
        :rtype dict:
        """
        values = {}

        for attributeValue in attributeValues.items():
            if attribute['id'] == attributeValue[1]['attributeId']:
                values.update({attributeValue[1]['id']: attributeValue[1]})
        return {'attributeValues': values}