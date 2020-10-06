from .models import Forum, Comment, Label
from .serializers import ForumSerializer, CommentSerializer, LabelSerializer
from rest_framework import status,filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from django.http import Http404
from .permissions import IsAuthor

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
        data['forum'] =parent_comment.forum.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            parent_comment.is_parent=True
            parent_comment.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_forum(self,forum_id):
        try:
            return Forum.objects.get(id=forum_id)
        except:
            raise Http404

    def get(self, request, forum_id, *args, **kwargs):
        forum = self.get_forum(forum_id)
        serializer = ForumSerializer(forum)
        votes = serializer.data.get('votes')
        return Response({'votes':votes},status=status.HTTP_200_OK)

    def post(self,request,forum_id,format=None):
        forum = self.get_forum(forum_id)
        value = int(request.data.get('vote'))
        if request.user.profile in forum.voter.all():
                return Response({'detail': "Already voted"},status=status.HTTP_400_BAD_REQUEST)
        if value > 0:
            forum.votes += 1
            forum.voter.add(request.user.profile)
            forum.save()
            return Response(status=status.HTTP_200_OK)
        forum.votes -= 1
        forum.voter.add(request.user.profile)
        forum.save()
        return Response(status=status.HTTP_200_OK)
        

class FilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, search, *args, **kwargs):
        try:
            label = Label.objects.get(label_name = search)
            forum_posts = Forum.objects.filter(tag  = label)
            serializer  = ForumSerializer(forum_posts, many = True, context = {'request': request})
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({"There is no post with given searched tag"},status = status.HTTP_204_NO_CONTENT)

class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_forum(self,forum_id):
        try:
            return Forum.objects.get(id=forum_id)
        except:
            raise Http404

    def post(self, request, forum_id, *args, **kwargs):
        forum = self.get_forum(forum_id)
        user  = request.user.profile
        print(user)
        print(forum)
        print(user in forum.bookmark.all())
        if user not in forum.bookmark.all():
            forum.bookmark.add(user)
            return Response({'msg': "Bookmark added"},status=status.HTTP_201_CREATED) 
        return Response({'msg': "Post already bookmarked"},status=status.HTTP_400_BAD_REQUEST)

