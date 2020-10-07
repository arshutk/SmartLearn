from library.serializer import DocumentSerializer, CommentSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404

from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly

class DocumentPostView(APIView):
    permission_classes = [IsAuthenticated]
    pass
