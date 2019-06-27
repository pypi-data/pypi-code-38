from django.db.models import Count, Q, F


from aparnik.contrib.suit.api.views import AdminListAPIView, ModelAdminSortAPIView
from aparnik.packages.shops.orders.models import Order
from .serializers import BaseModel, BaseModelAdminSerializer


class BaseModelSortAdminAPIView(ModelAdminSortAPIView):

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(BaseModelSortAdminAPIView, self).__init__(*args, **kwargs)
        command_dict = {
            'visit': {
                'label': 'تعداد نمایش',
                'queryset_filter': Q(),
                'annotate_command': {'sort_count': F('visit_count')},
                'key_sort': 'sort_count',
            },
            'bookmark':{
                'label': 'تعداد بوکمارک',
                'queryset_filter': Q(),
                'annotate_command': {'sort_count': Count('bookmark_obj')},
                'key_sort': 'sort_count',
            }
        }

        self.command_dict.update(command_dict)


class BaseModelAdminListAPIView(AdminListAPIView):
    serializer_class = BaseModelAdminSerializer
    queryset = BaseModel.objects.all()

    def get_sort_api(self, request):
        return BaseModelSortAdminAPIView(request=self.request)
