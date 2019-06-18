from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Lib.Mappers.AttributesMapper import AttributesMapper


class ProductAttributeValuesMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return AttributesMapper:
        """
        raw = {}
        i = 0

        try:
            if type(list(array.values())[0]) == str:
                array = {'0': array}
        except:
            pass

        for item in array.values():
            i += 1
            raw.update({str(i): {
                item.get('attributeId'): {
                    'id': item.get('attributeId'),
                    'title': item.get('title'),
                    'code': item.get('code'),
                    'showInSpecList': item.get('showInSpecList'),
                    'description': item.get('description'),
                    'attributeGroupId': item.get('attributeGroupId'),
                    'cssClass': item.get('cssClass'),

                    'attributeId': item.get('attributeId'),
                    'productId': item.get('productId'),

                    'attributeValues': {
                        'id': item.get('id'),
                        'value': item.get('value'),
                        'title': item.get('valueTitle'),
                        'image': item.get('image'),
                        'cssClass': item.get('valueCssClass'),
                        'unitOfMeasureId': item.get('unitOfMeasureId')
                    }
                }
            }})

        mapper = AttributesMapper()
        result = []

        for item in raw.values():

            if i == 1:
                result = mapper.createObject(item.get(list(item)[0]))
            else:
                result.append(mapper.createObject(item.get(list(item)[0])))

        return result
