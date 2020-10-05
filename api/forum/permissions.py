from rest_framework import permissions
from userauth.models import UserProfile

class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile == obj.author

