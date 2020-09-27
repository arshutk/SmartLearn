from django.shortcuts import render
from datetime import timedelta,datetime
from rest_framework import viewsets,status,generics
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
from userauth.serializers import UserProfileSerializer
from django.forms.models import model_to_dict
class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get_object(self,pk):
        try:
            return UserProfile.objects.get(pk=pk)
        except:
            raise Http404
    def get(self,request,pk,format=None):
        user_profile = self.get_object(pk)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data,status=status.HTTP_200_OK)

def get_random_string(length):
    """
    Returns Random String of given length
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class ClassroomViewSet(viewsets.ModelViewSet):
    model = Classroom
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    def get_queryset(self):
        queryset1 = Classroom.objects.filter(teacher=self.request.user.profile)
        queryset2 =  Classroom.objects.filter(student=self.request.user.profile)
        return queryset2 | queryset1
    def create(self, request):
        data = request.data
        teacher = request.user.profile.id
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
            permission_classes = [IsTeacher,IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [IsTeacherOrIsStudent]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsTeacher,IsAuthenticated]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    

class ClassjoinView(APIView):
    permission_classes=[IsAuthenticated,IsStudent]
    def post(self, request, format=None):
        class_code = request.data["class_code"]
        try:
            class_join = Classroom.objects.get(class_code=class_code)
        except:
            return Response({
                "error" : "No such class.",
                "user" : request.user.email
            },status=status.HTTP_400_BAD_REQUEST)
        current_user =  request.user.profile
        class_join.student.add(current_user)
        class_join.save()
        return Response({'class_id': class_join.id }, status=status.HTTP_201_CREATED)


class AssignmentPost(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Classroom.objects.get(pk=pk)
        except :
            raise Http404
    def get(self, request, pk, format=None):
        user_profile = request.user.profile
        classroom = self.get_object(pk)
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            assignment = Assignment.objects.filter(classroom=classroom)
            serializer = AssignmentSerializer(assignment,many=True)
            return Response(serializer.data)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    def post(self, request, pk, format=None):
        user_profile = request.user.profile
        classroom = self.get_object(pk)
        if user_profile == classroom.teacher:
            data=request.data
            data['classroom'] = classroom.id
            try:
               if data['submit_by'] <= datetime.now() + timedelta(minutes=2):
                   return Response({"details" : "submit_by can not be smaller than current time + 2 minutes."})
            except:
                pass
            serializer = AssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


class AssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk,id):
        try:
            classroom = Classroom.objects.get(pk=pk)
            assignment = Assignment.objects.get(classroom=classroom,pk=id)
            return classroom
        except :
            raise Http404
    
    def get(self,request,pk,id,format=None):
        classroom = self.get_object(pk,id)
        assignment = Assignment.objects.get(classroom=classroom,pk=id)
        user_profile = request.user.profile
        if user_profile == classroom.teacher or (user_profile in classroom.student.all()):
            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self,request,pk,id,format=None):
        classroom = self.get_object(pk,id)
        assignment = Assignment.objects.get(classroom=classroom,pk=id)
        user_profile = request.user.profile
        if user_profile == classroom.teacher:
            assignment.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
class AnswerSheetPost(APIView):
    permission_classes = [IsAuthenticated,IsStudent]
    def post(self,request,class_id,assignment_id,format=None):
        try: 
            classroom = Classroom.objects.get(pk=class_id)
            assignment = Assignment.objects.get(pk=assignment_id)
            user_profile = request.user.profile
        except:
            raise Http404
        if user_profile in classroom.student.all():
            try:
                AnswerSheet.objects.get(assignment=assignment,student=user_profile)
            except:
                data = request.data
                if assignment.submit_by:
                    if datetime.now() >= assignment.submit_by:
                        data['late_submitted'] == True
                data['student'] = user_profile.id
                data['assignment'] = assignment.id
                data['marks_scored'] = 0
                data['checked'] = False
                serializer = AnswerSheetSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"deatils" : "Already submitted."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            
class AnswerSheetView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, class_id,assignment_id,answer_id):
        try:
            
            classroom = Classroom.objects.get(pk=class_id)
            
            assignment = Assignment.objects.get(classroom=classroom,pk=assignment_id)
            
            answer = AnswerSheet.objects.get(assignment=assignment,pk=answer_id)
           
            return answer
        except :
            raise Http404
    
    def get(self,request,class_id,assignment_id,answer_id,format=None):
        user_profile = request.user.profile
        answer = self.get_object(class_id,assignment_id,answer_id)
        if user_profile == answer.assignment.classroom.teacher or user_profile == answer.student :
            serializer = AnswerSheetSerializer(answer)
            return Response(serializer.data)
        return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN) 
    
    def put(self,request,class_id,assignment_id,answer_id,format=None):
        user_profile = request.user.profile
        answer = self.get_object(class_id,assignment_id,answer_id)
        if  answer.checked == True:
            return Response({'details' : "already checked."},status = status.HTTP_400_BAD_REQUEST)
        if user_profile == answer.assignment.classroom.teacher:
            data=request.data
            try: 
                marks = data['marks_scored']
            except:
                return Response({"details" : "marks_scored field is required."}, status=status.HTTP_400_BAD_REQUEST)
            if marks <= answer.assignment.max_marks:
                answer.marks_scored = marks
                answer.checked = True
                answer.save()
                serializer = AnswerSheetSerializer(answer)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response({'details': "marks_scored should not be greater that max_marks"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"details": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)  


class ListOfAnswers(APIView):
    permission_classes = [IsTeacher]
    def get_object(self, class_id,assignment_id):
        try:
            classroom = Classroom.objects.get(pk=class_id)
            assignment = Assignment.objects.get(classroom=classroom,pk=assignment_id)
            return assignment
        except:
            raise Http404
    def get(self,request,class_id,assignment_id,format=None):
        user_profile = request.user.profile
        assignment = self.get_object(class_id, assignment_id)
        if user_profile == assignment.classroom.teacher:
            answers = AnswerSheet.objects.filter(assignment=assignment)
            serializer = AnswerSheetSerializer(answers,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"details" : "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
