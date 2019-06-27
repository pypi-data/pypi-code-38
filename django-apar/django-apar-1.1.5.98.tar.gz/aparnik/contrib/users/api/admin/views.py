from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce


from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.suit.api.views import ModelAdminSortAPIView
from aparnik.packages.shops.orders.models import Order
from aparnik.packages.educations.progresses.models import ProgressSummary
from .serializers import User, UserAdminListSerializer


class UserSortAdminAPIView(ModelAdminSortAPIView):

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(UserSortAdminAPIView, self).__init__(*args, **kwargs)

        command_dict = {
            # TODO: read bellow line
            # این گزارش باید بر اساس تاریخ به مدیر گفته شود
            'register_date': {
                'label': 'ثبت نام',
                'queryset_filter': Q(),
                'annotate_command': {'sort_count': F('created_at')},
                'key_sort': 'sort_count',
            },
            'qa': {
                'label': 'پرسش و پاسخ',
                'queryset_filter': Q(),
                'annotate_command': {'sort_count': Count('qa')},
                'key_sort': 'sort_count',
            },
            'reviews': {
                'label': 'نظر',
                'queryset_filter': Q(),
                'annotate_command': {'sort_count': Count('review')},
                'key_sort': 'sort_count',
            },

        }
        command_dict.update(ProgressSummary.sort_progress(prefix='progress_user'))
        command_dict.update(Order.sort_buy(prefix='order'))
        command_dict.update(Order.sort_buy_waiting(prefix='order'))
        command_dict.update(Order.sort_buy_wallet(prefix='order'))
        command_dict.update(Order.sort_buy_bank(prefix='order'))

        self.command_dict.update(command_dict)


class UserAdminListAPIView(AdminListAPIView):
    serializer_class = UserAdminListSerializer
    queryset = User.objects.all()

    def get_sort_api(self, request):
        return UserSortAdminAPIView(request=self.request)
