from rest_framework import permissions
from userauth.models import UserProfile

class IsTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile == obj.teacher
    def has_permission(self,request,view):
        return request.user.profile.is_teacher

class IsTeacherOrIsStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile in obj.student.all() or request.user.profile==obj.teacher

class IsStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile in obj.student.all() and (not request.user.profile.is_teacher)
    def has_permission(self,request,view):
        return not request.user.profile.is_teacher
