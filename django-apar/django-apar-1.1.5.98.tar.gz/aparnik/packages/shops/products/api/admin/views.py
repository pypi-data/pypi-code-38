from django.db.models import Count, Q


from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.basemodels.api.admin.views import BaseModelSortAdminAPIView
from aparnik.packages.shops.orders.models import Order
from .serializers import Product, ProductAdminListSerializer


class ProductSortAdminAPIView(BaseModelSortAdminAPIView):

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(ProductSortAdminAPIView, self).__init__(*args, **kwargs)
        command_dict = {

        }

        command_dict.update(Order.sort_buy_waiting(prefix='orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy(prefix='orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy_wallet(prefix='orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy_bank(prefix='orderitem_set__order_obj'))

        self.command_dict.update(command_dict)


class ProductAdminListAPIView(AdminListAPIView):
    serializer_class = ProductAdminListSerializer
    queryset = Product.objects.all()

    def get_sort_api(self, request):
        return ProductSortAdminAPIView(request=self.request)
