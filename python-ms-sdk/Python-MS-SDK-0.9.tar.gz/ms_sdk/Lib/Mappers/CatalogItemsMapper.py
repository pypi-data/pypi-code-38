import json
from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.CatalogItem import CatalogItem


class CatalogItemsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return CatalogItem:
        """
        catalogItem = CatalogItem(array)

        if catalogItem.filterSettings:
            catalogItem.filterSettings = json.loads(
                str(catalogItem.filterSettings))

        return catalogItem
