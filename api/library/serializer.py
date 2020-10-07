from rest_framework import serializers

from .models import Document, Comment

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields =  '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields =  '__all__'

