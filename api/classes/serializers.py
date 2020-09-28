from rest_framework import serializers

from .models import Classroom,Assignment,AnswerSheet, DoubtSection

from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from userauth.serializers import UserProfileSerializer

class ClassroomSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Classroom
        fields =('__all__')
        #fields = ('class_code','subject_name','subject_code','description','standard','branch','section')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['teacher'] = UserProfileSerializer(instance.teacher).data
        response['student'] = UserProfileSerializer(instance.student,many=True).data
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