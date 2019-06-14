from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.views.generic.edit import DeleteView

from acmin.models import Permission, PermissionItem
from .mixins import AccessMixin


class AdminDeleteView(AccessMixin, SuccessMessageMixin, DeleteView):
    success_message = "删除成功!"

    def has_permission(self):
        return Permission.has_permission(self.request.user, self.model, PermissionItem.removable)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return HttpResponse("ok")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view_type"] = 'delete'
        return context
