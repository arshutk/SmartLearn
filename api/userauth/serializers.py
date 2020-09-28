from rest_framework import serializers
from userauth.models import User, UserProfile
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.password_validation import validate_password

class UserProfileSerializer(serializers.ModelSerializer):    
    class Meta:
        model = UserProfile
        fields = ('id','name', 'picture','is_teacher')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'profile',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.name = profile_data.get('name', profile.name)
        profile.picture = profile_data.get('picture', profile.picture)
        profile.save()
