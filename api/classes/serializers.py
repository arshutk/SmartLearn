from rest_framework import serializers

from .models import Classroom,Assignment,AnswerSheet, DoubtSection

from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from userauth.serializers import UserProfileSerializer
from userauth.models import UserProfile
class ClassroomSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Classroom
        fields = ('id','class_code','subject_name','description','teacher','student')
        write_only_fields = ('student',)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['teacher'] = UserProfileSerializer(instance.teacher).data
       # response['student'] = UserProfileSerializer(instance.student,many=True).data
        return response

class AnswerSheetSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AnswerSheet
        fields =('__all__')
       

class AssignmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Assignment
        fields =('__all__')


class DoubtSectionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = DoubtSection
        fields =('__all__')

class Portal:
    def __init__(self, student, percentage, no_of_assignments,no_of_answers):
        self.student = student
        self.percentage = percentage
        self.no_of_assignments = no_of_assignments
        self.no_of_answers = no_of_answers


class StudentPortalSerializer(serializers.Serializer):
    student = serializers.IntegerField(read_only=True)
    percentage = serializers.DecimalField(read_only=True,max_digits=10,decimal_places=2)
    no_of_assignments = serializers.IntegerField(read_only=True)
    no_of_answers = serializers.IntegerField(read_only=True)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        student = UserProfile.objects.get(id=instance.student)
        response['student'] = UserProfileSerializer(student).data
        return response

