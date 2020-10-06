from rest_framework import serializers

from .models import Classroom,Assignment,AnswerSheet, DoubtSection,PrivateComment

from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from userauth.serializers import UserProfileSerializer
from userauth.models import UserProfile

class ClassroomSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Classroom
        fields = ('id','class_code','subject_name','description','teacher')
        write_only_fields = ('student',)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        # response['teacher'] = UserProfileSerializer(instance.teacher).data
        response['teacher'] = UserProfileSerializer(instance.teacher, context = {'request': self.context.get('request')}).data
        return response

class AnswerSheetSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AnswerSheet
        fields =('__all__')
    def to_representation(self,instance):
        response = super().to_representation(instance)
        response['student'] = UserProfileSerializer(instance.student, context = {'request': self.context.get('request')}).data
        return response
        
class AssignmentSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Assignment
        fields =('__all__')

class DoubtSectionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = DoubtSection
        fields =('__all__')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserProfileSerializer(instance.user, context = {'request': self.context.get('request')}).data
        # response['user'] = UserProfileSerializer(instance.user).data
        # response['classroom'] = ClassroomSerializer(instance.classroom).data
        return response

class PrivateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateComment
        fields = ('__all__')
    def to_representation(self,instance):
        response = super().to_representation(instance)
        response['sender'] = UserProfileSerializer(instance.sender, context={'request' : self.context.get('request')}).data
        response['receiver'] = UserProfileSerializer(instance.receiver, context={'request' : self.context.get('request')}).data
        return response