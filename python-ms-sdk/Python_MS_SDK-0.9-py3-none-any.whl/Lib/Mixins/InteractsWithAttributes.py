from ms_sdk.Entities.Attribute import Attribute
from ms_sdk.Entities.AttributeValue import AttributeValue


class InteractsWithAttributesMixin:

    def getAttributeById(self, id):
        """
        :param id:
        :return None|Attribute:
        """
        return self.getAttributeByFieldNameAndValue('id', id)

    def getAttributesByIds(self, ids):
        """
        :param ids:
        :return dict|Attribute{}:
        """
        return self.getAttributesByFieldNameAndValues('id', ids)

    def getAttributeByCode(self, code):
        """
        :param code:
        :return None|Attribute:
        """
        return self.getAttributeByFieldNameAndValue('code', code)

    def getAttributesByCodes(self, codes):
        """
        :param codes:
        :return dict|Attribute{}:
        """
        return self.getAttributesByFieldNameAndValues('code', codes)

    def getFirstValueByAttributeCode(self, code):
        """
        :param code:
        :return None|AttributeValue:
        """
        attribute = self.getAttributeByCode(code)

        try:
            values = attribute.values[0]
        except:
            values = attribute.values

        if not values:
            return None

        return values

    def getAttributeByFieldNameAndValue(self, fieldName, value):
        """
        :param string fieldName:
        :param value:
        :return None|Attribute:
        """
        if not self.attributes:
            return None

        for attribute in self.attributes:
            if str(eval('attribute.' + fieldName)) == str(value):
                return attribute

        return None

    def getAttributesByFieldNameAndValues(self, fieldName, value):
        """
        :param string fieldName:
        :param value:
        :return Attribute{}:
        """
        attributes = []

        if not self.attributes:
            return attributes

        for attribute in self.attributes:
            if (str(eval('attribute.' + fieldName)) in str(value)) or (str(eval('attribute.' + fieldName)) == str(value)):
                attributes.append(attribute)

        return attributes
