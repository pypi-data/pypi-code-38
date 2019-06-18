from ms_sdk.Lib.Mappers.Mapper import Mapper
from ms_sdk.Entities.OrderItem import OrderItem
from ms_sdk.Lib.Mappers.ProductsMapper import ProductsMapper


class OrderItemsMapper(Mapper):

    def doCreateObject(self, array):
        """
        :param dict array:
        :return OrderItem:
        """
        orderItem = OrderItem(array)

        try:
            first = array.get('products')[0]
        except:
            first = array

        if first:
            productMapper = ProductsMapper()

            if array.get('images'):
                array['products'][0]['images'] = array['images']

            orderItem.product = productMapper.createObject(first)

        return orderItem