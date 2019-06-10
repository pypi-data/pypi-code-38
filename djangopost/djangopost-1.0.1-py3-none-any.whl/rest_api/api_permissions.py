from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    message = "Only the owner of this post can modify it."

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        else:
            return False    