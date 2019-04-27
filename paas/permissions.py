from rest_framework import permissions


class ResourceOwnerReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.owner == request.user
