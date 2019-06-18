from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.Price.ProductPriceConfiguration import ProductPriceConfiguration


class ProductPriceConfigurationsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return ProductPriceConfiguration:
        """
        productPriceConfiguration = ProductPriceConfiguration(array)

        try:
            if array.get('prices').get('affectAttributes'):
                productPriceConfiguration.affectedAttributes = array.get('prices').get('affectAttributes')
        except:
            pass

        try:
            if array.get('prices').get('priceTable'):
                for priceKey, price in array.get('prices').get('priceTable'):
                    productPriceConfiguration.priceTable[priceKey] = price
        except:
            pass

        productPriceConfiguration.removeProperty('prices')
        return productPriceConfiguration