from rest_framework import serializers

from .models import Classroom,Assignment,AnswerSheet, DoubtSection, PrivateChat, PrivateComment

from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from userauth.serializers import UserProfileSerializer
from userauth.models import UserProfile

class ClassroomSerializer(serializers.ModelSerializer):  
    student_no    = serializers.SerializerMethodField('get_student_no')  

    class Meta:
        model = Classroom
        fields = ('id','class_code','subject_name','description','teacher','student_no')
        write_only_fields = ('student',)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['teacher']    = UserProfileSerializer(instance.teacher, context = {'request': self.context.get('request')}).data
        return response

    def get_student_no(self, obj):
        return obj.student.all().count()
        


class AnswerSheetSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AnswerSheet
        fields =('__all__')
    def to_representation(self,instance):
        response = super().to_representation(instance)
        response['student'] = UserProfileSerializer(instance.student, context = {'request': self.context.get('request')}).data
        return response
        
class AssignmentSerializer(serializers.ModelSerializer):  
    answer_id    = serializers.SerializerMethodField('get_answer_id')
    
    class Meta:
        model = Assignment
        fields =('id','title','description','time_created','submit_by','max_marks','file_linked','classroom','answer_id')

    def get_answer_id(self, obj):
        user = self.context.get('request').user
        if str(obj.classroom.teacher) != str(user):
            try:
                if not obj.answersheet.all():
                    return None
                for answer in obj.answersheet.all():
                    if str(answer.student) == str(user):
                        return answer.id
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

class PrivateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateComment
        fields = ('__all__')
    def to_representation(self,instance):
        response = super().to_representation(instance)
        response['sender'] = UserProfileSerializer(instance.sender, context={'request' : self.context.get('request')}).data
        response['receiver'] = UserProfileSerializer(instance.receiver, context={'request' : self.context.get('request')}).data
        return response

class PrivateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateChat
        fields =('__all__')
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['sender']     = UserProfileSerializer(instance.sender, context = {'request': self.context.get('request')}).data
        response['reciever']   = UserProfileSerializer(instance.reciever, context = {'request': self.context.get('request')}).data
        response['classroom']  = ClassroomSerializer(instance.classroom, context = {'request': self.context.get('request')}).data
        return response