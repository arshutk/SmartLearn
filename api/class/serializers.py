from rest_framework import serializers
from .models import Classroom
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings


class ClassroomSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Classroom
        fields = ('__all__')