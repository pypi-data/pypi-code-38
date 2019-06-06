from guardian.shortcuts import get_objects_for_user
from rest_framework import filters
from rest_framework import permissions

from djangoldp.models import Model

"""
Liste des actions passées dans views selon le protocole REST :
    list
    create
    retrieve
    update, partial update
    destroy
Pour chacune de ces actions, on va définir si on accepte la requête (True) ou non (False)
"""
"""
    The instance-level has_object_permission method will only be called if the view-level has_permission 
    checks have already passed
"""


class WACPermissions(permissions.DjangoObjectPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        else:
            return super().has_permission(request, view)

    # This method should be overriden by other permission classes
    def user_permissions(self, user, obj):
        return []

    def filter_user_perms(self, user_or_group, obj, permissions):
        return [perm for perm in permissions if perm in self.user_permissions(user_or_group, obj)]


class ObjectFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
            Ensure that queryset only contains objects visible by current user
        """
        perm = "view_{}".format(queryset.model._meta.model_name.lower())
        objects = get_objects_for_user(request.user, perm, klass=queryset)
        return objects


class ObjectPermission(WACPermissions):
    filter_class = ObjectFilter


class InboxPermissions(WACPermissions):
    """
        Everybody can create
        Author can edit
    """
    anonymous_perms = ['create']
    authenticated_perms = ['create']
    author_perms = ['view', 'update']

    def has_permission(self, request, view):
        if view.action in ['create']:
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'partial_update', 'destroy']:
            return False
        else:
            return super().has_object_permission(request, view, obj)

    def user_permissions(self, user, obj):
        if user.is_anonymous:
            return self.anonymous_perms
        else:
            if Model.get_meta(obj, 'auto_author') == user:
                return self.author_perms
            else:
                return self.authenticated_perms


class AnonymousReadOnly(WACPermissions):
    """
        Anonymous users: can read all posts
        Logged in users: can read all posts + create new posts
        Author: can read all posts + create new posts + update their own
    """

    anonymous_perms = ['view']
    authenticated_perms = ['view', 'add']
    author_perms = ['view', 'add', 'change', 'control', 'delete']

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action == 'create' and request.user.is_authenticated():
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action == "create" and request.user.is_authenticated():
            return True
        elif view.action in ["list", "retrieve"]:
            return True
        elif view.action in ['update', 'partial_update', 'destroy']:
            if hasattr(obj._meta, 'auto_author'):
                author = getattr(obj, obj._meta.auto_author)
                if author == request.user:
                    return True
        else:
            return super().has_object_permission(request, view, obj)

    def user_permissions(self, user, obj):
        if user.is_anonymous:
            return self.anonymous_perms
        else:
            if Model.get_meta(obj, 'auto_author') == user:
                return self.author_perms
            else:
                return self.authenticated_perms


class LoggedReadOnly(WACPermissions):
    """
        Anonymous users: Nothing
        Logged in users: can read all posts
    """

    anonymous_perms = []
    authenticated_perms = ['view']

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve'] and request.user.is_authenticated():
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action in ["list", "retrieve"] and request.user.is_authenticated():
            return True
        else:
            return super().has_object_permission(request, view, obj)

    def user_permissions(self, user, obj):
        if user.is_anonymous:
            return self.anonymous_perms
        else:
            return self.authenticated_perms
