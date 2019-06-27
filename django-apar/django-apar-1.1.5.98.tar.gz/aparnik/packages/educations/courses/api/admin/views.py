from django.db.models import Sum, Q
from django.db.models.functions import Coalesce


from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.packages.shops.products.api.admin.views import ProductSortAdminAPIView
from aparnik.packages.educations.progresses.models import ProgressSummary
from .serializers import Course, CourseAdminListSerializer


class CourseSortAdminAPIView(ProductSortAdminAPIView):

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(CourseSortAdminAPIView, self).__init__(*args, **kwargs)
        command_dict = {

        }
        self.command_dict.update(ProgressSummary.sort_progress(prefix='progress_summaries'))
        self.command_dict.update(command_dict)


class CourseAdminListAPIView(AdminListAPIView):
    serializer_class = CourseAdminListSerializer
    queryset = Course.objects.all()

    def get_sort_api(self, request):
        return CourseSortAdminAPIView(request=self.request)
