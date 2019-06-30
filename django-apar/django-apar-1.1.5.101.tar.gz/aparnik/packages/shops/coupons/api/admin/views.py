from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce

from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.basemodels.api.admin.views import BaseModelSortAdminAPIView
from aparnik.packages.shops.orders.models import Order
from .serializers import Coupon, CouponAdminListSerializer


class CouponSortAdminAPIView(BaseModelSortAdminAPIView):
    """
        A view that returns the count of active users in JSON.
        """

    def __init__(self, *args, **kwargs):
        super(CouponSortAdminAPIView, self).__init__(*args, **kwargs)

        command_dict = {}
        command_dict.update(Coupon.sort_redeem(prefix='membership'))
        self.command_dict = command_dict


class CouponAdminListAPIView(AdminListAPIView):
    serializer_class = CouponAdminListSerializer
    queryset = Coupon.objects.all()

    def get_sort_api(self, request):
        return CouponSortAdminAPIView(request=request)
