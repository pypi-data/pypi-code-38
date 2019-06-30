from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce

from aparnik.contrib.suit.api.views import AdminListAPIView
from aparnik.contrib.suit.api.views import ModelAdminSortAPIView
from .serializers import Audit, AuditAdminListSerializer


class AuditSortAdminAPIView(ModelAdminSortAPIView):

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(AuditSortAdminAPIView, self).__init__(*args, **kwargs)

        command_dict = {

        }
        # this name of
        command_dict.update(Audit.sort_audit(type=Audit.ACTION_LOGIN))
        command_dict.update(Audit.sort_audit(type=Audit.ACTION_LOGOUT))
        command_dict.update(Audit.sort_audit(type=Audit.ACTION_LOGIN_FAILED))
        self.command_dict.update(command_dict)


class AuditAdminListAPIView(AdminListAPIView):
    serializer_class = AuditAdminListSerializer
    queryset = Audit.objects.all()

    def get_sort_api(self, request):
        return AuditSortAdminAPIView(request=self.request)
