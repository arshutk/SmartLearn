from .models import Forum, Comment, Label
from .serializers import ForumSerializer, CommentSerializer, LabelSerializer

from rest_framework.response import Response

# pass context = {'request' : request} everywhere you instantiate a Serializer for absolute url