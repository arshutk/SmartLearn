from rest_framework import permissions
from userauth.models import UserProfile

class IsTeacher(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        return user == obj.teacher

class IsStudent(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = UserProfile.objects.get(user=request.user)
        return user in obj.student.all()

class IsClassroomMember(permissions.BasePermission):
    pass
    
#     def has_permission(self,request,view):
#         poster = request.user.id
#         data = request.data
#         classroom = data['classroom']
#         # teacher_name = Classroom.objects.get(id = classroom).teacher
#         # teacher_email = UserProfile.objects.filter(name = teacher_name)[0]
#         # student = Classroom.objects.get(id = classroom).student.all()
#         poster_ = UserProfile.objects.get(id = poster)

#         print(poster.id)
#         print(data)
#         print(student)
#         print(teacher_name) 
#         print(teacher_email) 
#         # print(poster == teacher)
#         print(list(student))
#         print(poster in list(student))

        