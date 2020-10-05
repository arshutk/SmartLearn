from rest_framework import serializers

from forum.models import Forum, Comment, Label

from userauth.serializers import UserProfileSerializer

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ('title','text','image','upvotes','tag','author')
        write_only_fields = ('upvotees',)
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['author'] = UserProfileSerializer(instance.author,context = {'request' : self.context.get('request')}).data
        response['tag'] = LabelSerializer(instance.tag).data
        response['comment_count'] = instance.comments.count()
        return response


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['child_comments'] = CommentSerializer(instance.child_comments.all(),many=True).data
        return response


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'
