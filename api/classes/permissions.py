from rest_framework import permissions
from userauth.models import UserProfile

class IsTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        print(user,obj.teacher,user==obj.teacher)
        return user == obj.teacher
    def has_permission(self,request,view):
        user = UserProfile.objects.get(user=request.user)
        return user.is_teacher

class IsTeacherOrIsStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        return user in obj.student.all() or user==obj.teacher

class IsStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        return user in obj.student.all() and (not user.is_teacher)
    def has_permission(self,request,view):
        user = UserProfile.objects.get(user=request.user)
        return not user.is_teacher
