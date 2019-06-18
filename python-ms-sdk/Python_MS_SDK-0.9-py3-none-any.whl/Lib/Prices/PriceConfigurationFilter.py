from ms_sdk.Exceptions.SMSDKException import SMSDKException


class PriceConfigurationFilter:

    products = []

    def addProduct(self, product):
        """
        :param product:
        """
        self.products.append(product)

    def getData(self):
        """
        :raises SMSDKException:
        :rtype dict:
        """
        if not self.products:
            raise SMSDKException('Property products is empty. Add at least one product for filtering')

        data = []

        for product in self.products:
            data.append({
                'priceTypeId': product.priceTypeId,
                'productId': product.productId
            })

            return {'filters': data}