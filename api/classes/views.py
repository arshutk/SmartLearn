from django.shortcuts import render
from datetime import timedelta,datetime
from rest_framework import viewsets,status
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from userauth.models import UserProfile
from .models import Classroom,AnswerSheet,Assignment
from .permissions import IsStudent,IsTeacher,IsTeacherOrIsStudent
from .serializers import ClassroomSerializer,AnswerSheetSerializer,AssignmentSerializer
from userauth.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.response import Response
from django.http import Http404
import string
import random
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class ClassroomViewSet(viewsets.ModelViewSet):
    model = Classroom
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    def get_queryset(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)
        queryset1 = Classroom.objects.filter(teacher=user_profile)
        queryset2 =  Classroom.objects.filter(student=user_profile)
        return queryset2 | queryset1
    def create(self, request):
        data = request.data
        user = request.user
        teacher = UserProfile.objects.get(user=user).pk
        random_code = get_random_string(6)
        while(Classroom.objects.filter(class_code=random_code)) :
            random_code = get_random_string(6)
        data['class_code'] = random_code
        data['teacher'] = teacher
        data['student'] = []
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [IsTeacherOrIsStudent]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsTeacherOrIsStudent,IsAuthenticated]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    

class ClassjoinView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        class_code = request.data["class_code"]
        try:
            class_join = Classroom.objects.get(class_code=class_code)
        except:
            return Response({
                "error" : "No such class.",
                "user" : request.user.email
            },status=status.HTTP_400_BAD_REQUEST
            )
        current_user =  UserProfile.objects.get(user=request.user)
        if current_user == class_join.teacher:
            return Response({'datail' : 'you do not have permission to perform this action.'})
        class_join.student.add(current_user)
        class_join.save()
        return Response({'detail': f'{ request.user.email } {request.user.id} joined {class_join.id} succesfully'}, status=status.HTTP_201_CREATED)



class AnswerSheetViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    model = AnswerSheet
    queryset = AnswerSheet.objects.all()
    serializer_class = AnswerSheetSerializer
    
class AnswerSheetPost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,class_id,assignment_id,format=None):
        try: 
            classroom = Classroom.objects.get(pk=class_id)
            assignment = Assignment.objects.get(pk=assignment_id)
            user_profile = UserProfile.objects.get(user=request.user)
        except:
            raise Http404
        if user_profile in classroom.student.all():
            data = request.data
            if assignment.submit_by:
                if datetime.now() >= assignment.submit_by:
                    data['late_submitted'] == True
            data['student'] = user_profile.id
            data['assignment'] = assignment.id
            data['marks_scored'] = 0
            serializer = AnswerSheetSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
             

class AssignmentPost(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, format=None):
        try:
            classroom = Classroom.objects.get(pk=pk)
        except :
            raise Http404
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            assignment = Assignment.objects.filter(classroom=classroom)
            serializer = AssignmentSerializer(assignment,many=True)
            return Response(serializer.data)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, pk, format=None):
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            classroom = Classroom.objects.get(pk=pk,teacher=user_profile)  
        except:
            raise Http404
       
        if user_profile == classroom.teacher:
            data=request.data
            data['classroom'] = classroom.id
            serializer = AssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

class AssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,pk,id,format=None):
        try:
            classroom = Classroom.objects.get(pk=pk)
            assignment = Assignment.objects.get(classroom=classroom,pk=id)
        except :
            raise Http404
        user_profile = UserProfile.objects.get(user=request.user)
        print(classroom.id,assignment.id,user_profile.id,Classroom.teacher,user_profile in classroom.student.all())
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
