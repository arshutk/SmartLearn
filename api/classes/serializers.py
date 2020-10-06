from rest_framework import serializers

from .models import Classroom,Assignment,AnswerSheet, DoubtSection

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
    is_attempted = serializers.SerializerMethodField('get_is_attempted')

    class Meta:
        model = Assignment
        fields =('id','title','description','time_created','submit_by','max_marks','file_linked','classroom','is_attempted')
    
    def get_is_attempted(self, obj):
        user = self.context.get('request').user
        if str(obj.classroom.teacher) != str(user):
            try:
                if not obj.answersheet.all():
                    return False
                for answer in obj.answersheet.all():
                    if str(answer.student) == str(user):
                        return True
            except:
                pass
        else:
            return None
        

class DoubtSectionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = DoubtSection
        fields =('__all__')
        
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserProfileSerializer(instance.user, context = {'request': self.context.get('request')}).data
        return response


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
        response['student'] = UserProfileSerializer(student, context = {'request': self.context.get('request')}).data
        return response

