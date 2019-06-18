from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Lib.Mappers.AttributesMapper import AttributesMapper


class FacetAttributesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributesMapper:
        """
        raw = []

        for item in array:
            raw.append({
                item.get('attributeId'): {
                    'id': item.get('attributeId'),
                    'title': item.get('title'),
                    'code': item.get('code'),
                    'cssClass': item.get('cssClass'),

                    'attributeValues': {
                        'id': item.get('id'),
                        'value': item.get('value'),
                        'title': item.get('valueTitle'),
                        'amount': item.get('amount')
                    }
            }})

        mapper = AttributesMapper()
        result = []

        for item in raw:
            item = item[list(item)[0]]
            result.append(mapper.createObject(item))

        return result