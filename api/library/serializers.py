from rest_framework import serializers

from library.models import Document, Comment, College

from userauth.serializers import UserProfileSerializer


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields =  ('id','title','description','file','stars','category','college','uploader')
        write_only_fields = ('bookmark','voter',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['uploader'] = UserProfileSerializer(instance.uploader,context = {'request' : self.context.get('request')}).data
        response['college']  = CollegeSerializer(instance.college,   context = {'request' : self.context.get('request')}).data
        return response

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields =  ('id','text','document','commenter',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['document'] = DocumentSerializer(instance.document,context = {'request' : self.context.get('request')}).data
        response['commenter'] = UserProfileSerializer(instance.commenter,context = {'request' : self.context.get('request')}).data
        return response

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields =  ('__all__')