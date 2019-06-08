import rules
from rest_framework.permissions import SAFE_METHODS, BasePermission

from pretalx.person.permissions import can_change_submissions, is_object


class EventPermission(BasePermission):
    def get_permission_name(self, request, view):
        permission = getattr(self, f'{self.action}_permission')
        if permission:
            return permission
        if request.method not in SAFE_METHODS:
            return getattr(
                view, 'write_permission_required', getattr(view, 'permission_required')
            )
        return getattr(view, 'permission_required')

    def has_permission(self, request, view):
        permission = self.get_permission_name(request, view)
        if permission is None:
            return True
        if hasattr(self, f'get_{self.action}_permission_object'):
            obj = getattr(self, f'get_{self.action}_permission_object')()
        else:
            obj = request.event
        return request.user.has_perm(permission, obj)

    def has_object_permission(self, request, view, obj):
        permission = self.get_permission_name(request, view)
        if not permission:
            return True
        return request.user.has_perm(permission, obj)


rules.add_perm('api.change_speaker', is_object | can_change_submissions)
