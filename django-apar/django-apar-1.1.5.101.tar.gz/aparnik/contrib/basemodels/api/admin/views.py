from django.db.models import Count, Q, F


from aparnik.contrib.basemodels.models import BaseModel
from aparnik.contrib.bookmarks.models import Bookmark
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

        }
        self.command_dict.update(BaseModel.sort_visit())
        self.command_dict.update(Bookmark.sort_bookmark(prefix='bookmark_obj'))
        self.command_dict.update(command_dict)


class BaseModelAdminListAPIView(AdminListAPIView):
    serializer_class = BaseModelAdminSerializer
    queryset = BaseModel.objects.all()

    def get_sort_api(self, request):
        return BaseModelSortAdminAPIView(request=self.request)
