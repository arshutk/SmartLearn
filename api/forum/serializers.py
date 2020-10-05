from rest_framework import serializers

from forum.models import Forum, Comment, Label

from userauth.serializers import UserProfileSerializer

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserProfileSerializer(instance.user).data
        response['tag'] = LabelSerializer(instance.tag).data
        return response


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['parent_comment'] = CommentSerializer(instance.parent_comment).data
        return response


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'
