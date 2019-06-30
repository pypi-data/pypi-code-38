from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce

from aparnik.contrib.basemodels.models import BaseModel
from aparnik.contrib.bookmarks.models import Bookmark
from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.basemodels.api.admin.views import BaseModelSortAdminAPIView
from aparnik.packages.shops.orders.models import Order
from aparnik.packages.educations.progresses.models import ProgressSummary
from .serializers import Teacher, TeacherAdminListSerializer


class TeacherSortAdminAPIView(BaseModelSortAdminAPIView):
    """
        A view that returns the count of active users in JSON.
        """

    def __init__(self, *args, **kwargs):
        super(TeacherSortAdminAPIView, self).__init__(*args, **kwargs)

        command_dict = {
            'course_notify_me': {
                'label': 'مرا با خبر کن',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Count('course__notifyme_model')
                },
                'key_sort': 'sort_count',
            },
            'course_qa_replay': {
                'label': 'پاسخ مدرس',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Count('course__question_answers_set__parent_obj', filter=Q(
                            Q(course__question_answers_set__parent_obj__isnull=False),
                            Q(course__question_answers_set__user_obj=F('user_obj'))
                        ))
                },
                'key_sort': 'sort_count',
            },

        }

        command_dict.update(BaseModel.sort_visit(prefix='course', return_key='course_visit'))
        command_dict.update(Bookmark.sort_bookmark(return_key='course_bookmark', prefix='course__bookmark_obj'))
        command_dict.update(ProgressSummary.sort_progress(prefix='course__progress_summaries'))
        command_dict.update(ProgressSummary.sort_user_participation(prefix='course__progress_summaries'))
        command_dict.update(Order.sort_buy(prefix='course__orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy_waiting(prefix='course__orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy_wallet(prefix='course__orderitem_set__order_obj'))
        command_dict.update(Order.sort_buy_bank(prefix='course__orderitem_set__order_obj'))

        self.command_dict.update(command_dict)


class TeacherAdminListAPIView(AdminListAPIView):
    serializer_class = TeacherAdminListSerializer
    queryset = Teacher.objects.all()

    def get_sort_api(self, request):
        return TeacherSortAdminAPIView(request=self.request)
