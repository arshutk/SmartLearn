from rest_framework import serializers

from forum.models import Forum, Comment, Label

from userauth.serializers import UserProfileSerializer

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ('id','title','text','image','tag','author')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['author'] = UserProfileSerializer(instance.author,context = {'request' : self.context.get('request')}).data
        response['tag']    = LabelSerializer(instance.tag).data
        response['upvotes'] = instance.upvotees.count()
        response['downvotes'] = instance.downvotees.count()
        response['comment_count']  = instance.comments.count()
        response['bookmark_count'] = instance.bookmark.count()
        return response


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id','text','is_parent','forum','parent_comment')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['count_child_comments'] = instance.child_comments.count()
        return response


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'
