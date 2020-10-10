from .models import Forum, Comment, Label
from .models import UserProfile
from .serializers import ForumSerializer, CommentSerializer, LabelSerializer
from rest_framework import status,filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from django.http import Http404
from .permissions import IsAuthor
from django.db.models import Count
class ForumView(ModelViewSet):
    queryset = Forum.objects.all().annotate(upvotes=Count('upvotees'),downvotes=Count('downvotees')).order_by('-upvotes','downvotes')
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
        instance = self.get_object()
        serializer = self.get_serializer(instance) 
        comments = CommentSerializer(instance.comments.all().filter(parent_comment=None),many=True)
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
    def get(self,request,blog,format=None):
        blog=self.get_blog(blog)
        comments=blog.comments.all()
        serializer = CommentSerializer(comments,many=True)
        return Response(serializer.data)
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
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_forum(self,forum_id):
        try:
            return Forum.objects.get(id=forum_id)
        except:
            raise Http404

    def get(self, request, forum_id, *args, **kwargs):
        forum = self.get_forum(forum_id)
        upvotes = forum.upvotees.count()
        downvotes = forum.downvotees.count()
        return Response({'upvotes':upvotes,'downvotes':downvotes},status=status.HTTP_200_OK)
    def patch(self,request,forum_id,format=None):
        upvotee = request.user.profile
        forum = self.get_forum(forum_id)
        if upvotee in forum.downvotees.all():
            forum.downvotees.remove(upvotee)
        if upvotee in forum.upvotees.all():
            return Response({'detail': 'Already Upvoted'},status=status.HTTP_400_BAD_REQUEST)
        forum.upvotees.add(upvotee)
        return Response({'detail' : 'Upvoted'},status=status.HTTP_201_CREATED)  
    def put(self,request,forum_id,format=None):
        downvotee = request.user.profile
        forum = self.get_forum(forum_id)
        if downvotee in forum.upvotees.all():
            forum.upvotees.remove(downvotee)
        if downvotee in forum.downvotees.all():
            return Response({'detail': 'Already Downvoted'},status=status.HTTP_400_BAD_REQUEST)
        forum.downvotees.add(downvotee)
        return Response({'detail' : 'Downvoted'},status=status.HTTP_201_CREATED)

class FilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, search, *args, **kwargs):
        try:
            label = Label.objects.get(label_name = search)
            forum_posts = Forum.objects.filter(tag  = label).annotate(upvotes=Count('upvotees'),downvotes=Count('downvotees')).order_by('-upvotes','downvotes')
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

    def delete(self, request, forum_id):
        forum = self.get_forum(forum_id)
        user  = request.user.profile
        if user in forum.bookmark.all():
            forum.bookmark.remove(user)
            return Response({'msg': "Bookmark removed"},status=status.HTTP_201_CREATED) 
        return Response({'msg': "Post is not bookmarked"},status=status.HTTP_400_BAD_REQUEST)

class GetBookmarks(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(id = user_id)
        except:
            raise Http404

    def get(self, request, user_id, *args, **kwargs):
        user = self.get_user(user_id)
        forum = ForumSerializer(user.bookmarked.all().annotate(upvotes=Count('upvotees'),downvotes=Count('downvotees')).order_by('-upvotes','downvotes'), many = True, context = {'request':request})
        data = forum.data.copy()
        return Response(data, status = status.HTTP_200_OK)

class SharePostView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, post_id):
        return Response({'share': request.META['HTTP_HOST'] + request.get_full_path()}, status = status.HTTP_200_OK)

