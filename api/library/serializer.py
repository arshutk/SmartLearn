from rest_framework import serializers

from library.models import Document, Comment

from userauth.serializers import UserProfileSerializer


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields =  ('id','title','description','file','stars','category','college','uploader')
        write_only_fields = ('bookmark','voter',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['uploader'] = UserProfileSerializer(instance.uploader,context = {'request' : self.context.get('request')}).data
        # response['bookmark'] = UserProfileSerializer(instance.bookmark,context = {'request' : self.context.get('request')}).data
        # response['voter']    = UserProfileSerializer(instance.voter,   context = {'request' : self.context.get('request')}).data
        # print(response)
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

