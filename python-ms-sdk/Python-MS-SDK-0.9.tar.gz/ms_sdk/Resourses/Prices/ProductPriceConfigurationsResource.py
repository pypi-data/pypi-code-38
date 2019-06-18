from ms_sdk.Exceptions.EntityNotFoundException import EntityNotFoundException
from ms_sdk.Exceptions.MethodNotFoundException import MethodNotFoundException
from ms_sdk.Lib.Prices.PriceConfigurationFilter import PriceConfigurationFilter
from ms_sdk.Resourses import Resource


class ProductPriceConfigurationsResource(Resource):

    def getURI(self):
        return 'findprice'

    def create(self, data):
        """
        :raises MethodNotFoundException:
        :param data:
        """
        raise MethodNotFoundException('Method create() can not be use with product price configurations')

    def get(self, id):
        """
        :raises MethodNotFoundException:
        :param id:
        """
        raise MethodNotFoundException('Method get() can not be use with product price configurations')

    def update(self, id, data):
        """
        :raises MethodNotFoundException:
        :param id:
        :param data:
        """
        raise MethodNotFoundException('Method update() can not be use with product price configurations')

    def delete(self, id):
        """
        :raises MethodNotFoundException:
        :param id:
        """
        raise MethodNotFoundException('Method delete() can not be use with product price configurations')

    def findPrice(self, priceConfigurationFilter):
        """
        :raises SMSDKException:
        :param PriceConfigurationFilter priceConfigurationFilter:
        :return list|ProductPriceConfiguration[]:
        """
        data = priceConfigurationFilter.getData()

        response = self.handler.handle('POST', data)

        if not response.getSuccess():
            raise EntityNotFoundException(response.getErrorMessage())
        return self.make(response)

    def findProductPrice(self, product):
        """
        :param PriceProduct product:
        :raises SMSDKException:
        :return ProductPriceConfiguration|None:
        """
        priceConfigurationFilter = PriceConfigurationFilter()
        priceConfigurationFilter.addProduct(product)
        result = self.findPrice(priceConfigurationFilter)

        try:
            return result[0]
        except:
            if result:
                return result
        return None
