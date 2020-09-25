from rest_framework import permissions

class IsLoggedInUserOrAdmin(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff

class IfUserPasswordReset(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        return user and obj.user