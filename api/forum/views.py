from .models import Forum, Comment, Label
from .serializers import ForumSerializer, CommentSerializer, LabelSerializer
from rest_framework import status,filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from django.http import Http404
from .permissions import IsAuthor
# pass context = {'request' : request} everywhere you instantiate a Serializer for absolute url

class ForumView(ModelViewSet):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title']
    def create(self,request,*args, **kwargs):
        data=request.data
        author = request.user.profile
        data['author'] = author.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def retrieve(self, request, *args, **kwargs):
        print("calling retrieve")
        instance = self.get_object()
        serializer = self.get_serializer(instance) 
        comments = CommentSerializer(instance.comments.all().filter(is_parent=True),many=True)
        return Response({'blog': serializer.data, 'comments': comments.data})
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdminUser,IsAuthor]
        elif self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_blog(self,blog):
        try:
            return Forum.objects.get(id=blog)
        except:
            raise Http404
    # def get(self,request,blog,format=None):
    #     blog=self.get_blog(blog)
    #     comments=blog.comments.all()
    #     serializer = CommentSerializer(comments,many=True)
    #     return Response(serializer.data)
    def post(self,request,blog,format=None):
        blog_id=self.get_blog(blog).id
        data=request.data
        data['author'] =  request.user.profile.id
        data['forum'] = blog_id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CommentOnComment(APIView):
    permission_classes = [IsAuthenticated]
    def get_parent_comment(self,comment_id,blog):
        try:
            return Forum.objects.get(id=blog).comments.get(id=comment_id)
        except:
            raise Http404
    def post(self,request,comment_id,format=None):
        parent_comment= self.get_parent_comment(comment_id,blog)
        data=request.data
        data['author'] =  request.user.profile.id
        data['parent_comment'] = parent_comment.id
        datea['forum'] =parent_comment.forum.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            parent_comment.is_parent=True
            parent_comment.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UpvoteView(APIView):
    permission_classes=[IsAuthenticated]
    def get_forum(self,forum_id):
        try:
            return Forum.objects.get(id=forum_id)
        except:
            raise Http404
    def post(self,request,forum_id,format=None):
        forum= self.get_forum(forum_id)
        if request.user.profile in forum.upvotes.all():
            return Response({'detail': "Already upvoted"},status=status.HTTP_400_BAD_REQUEST)
        forum.upvote+=1
        forum.upvotes.add(request.user.profile)
        forum.save()
        return Response(status=status.HTTP_200_OK)

        