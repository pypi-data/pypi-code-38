from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.basemodels.api.admin.views import BaseModelSortAdminAPIView

from .serializers import Order, OrderAdminListSerializer


class OrderSortAdminAPIView(BaseModelSortAdminAPIView):
    """
        A view that returns the count of active users in JSON.
        """

    def __init__(self, *args, **kwargs):
        super(OrderSortAdminAPIView, self).__init__(*args, **kwargs)
        command_dict = {

        }
        command_dict.update(Order.sort_buy_waiting())
        command_dict.update(Order.sort_buy())
        command_dict.update(Order.sort_buy_wallet())
        command_dict.update(Order.sort_buy_bank())

        self.command_dict.update(command_dict)


class OrderAdminListAPIView(AdminListAPIView):
    serializer_class = OrderAdminListSerializer
    queryset = Order.objects.all()

    def get_sort_api(self, request):
        return OrderSortAdminAPIView(request=self.request)
