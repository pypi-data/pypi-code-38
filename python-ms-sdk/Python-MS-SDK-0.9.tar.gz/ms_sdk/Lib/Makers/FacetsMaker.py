from ms_sdk.Lib.Http.Response import Response
from ms_sdk.Lib.Makers.ObjectMaker import ObjectMaker
from ms_sdk.Lib.Mappers.FacetAttributesMapper import FacetAttributesMapper


class FacetsMaker(ObjectMaker):

    def makeSingle(self, response: Response):
        """
        :param Response response:
        :return:
        """
        if not response.getSuccess():
            return None

        result = {}
        data = response.getData()

        for itemsType, items in data.items():
            if itemsType == 'attributes':
                mapper = FacetAttributesMapper()
                result['attributes'] = mapper.createObject(items)
            elif itemsType == 'priceRange':
                result['priceRange'] = items

        return result