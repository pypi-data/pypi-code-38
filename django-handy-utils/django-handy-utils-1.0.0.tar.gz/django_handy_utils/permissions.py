from rest_framework import permissions
from django.core.exceptions import PermissionDenied

def permission_checker(perm):
    def wrapped_decorator(func):
        def wrapped_mutation(cls, root, info, **input):
            # make sure of these arguments to the wrapped mutation
            user = info.context.user
            if isinstance(perm, str):
                perms = (perm,)
            else:
                perms = perm

            if user.has_perms(perms):
                return func(cls, root, info, **input)
            raise PermissionDenied("Permission Denied.")

        return wrapped_mutation

    return wrapped_decorator

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class BaseModelPermissions(permissions.DjangoModelPermissions):

    def get_custom_perms(self, method, view):
        app_name = view.model._meta.app_label
        return [app_name + "." + perms for perms in view.extra_perms_map.get(method, [])]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, view.model)
        perms.extend(self.get_custom_perms(request.method, view))
        return (
                request.user and
                (request.user.is_authenticated() or not self.authenticated_users_only) and
                request.user.has_perms(perms)
        )
