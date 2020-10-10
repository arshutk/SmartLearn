from library.serializers import DocumentSerializer, CommentSerializer, CollegeSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404

from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly

from library.models import Document, Comment, College

from userauth.models import UserProfile

from rest_framework import generics


class DocumentView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        category = self.request.GET.get('category','')
        college  = self.request.GET.get('college','')
        stars    = self.request.GET.get('stars','')

        if category:
            if college is None and stars is None:
                queryset = queryset.filter(category__icontains = category)
            elif college:
                queryset = queryset.filter(category__icontains = category, college = college)
            else:
                queryset = queryset.filter(category__icontains = category, stars = stars)
            return queryset
        elif college: 
            if stars:
                queryset = queryset.filter(college = college, stars = stars)
            queryset = queryset.filter(college = college)
            return queryset
        else:
            queryset = queryset.filter(stars = stars)
        return queryset
    
    def post(self, request):
        data = request.data
        data['uploader'] = request.user.profile.id
        serializer = DocumentSerializer(data = data, context = {'request': request})
        print(serializer.initial_data)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()   
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_201_CREATED)

class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, doc_id):
        data = Comment.objects.all()
        serializer = CommentSerializer(data, many = True, context = {'request': request})
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, doc_id):
        data = request.data.copy()
        try:
            data['document'] = Document.objects.get(pk = doc_id).id
        except:
            raise Http404
        if not (request.user.profile in [comment.commenter for comment in Comment.objects.filter(document = doc_id)]):
            data['commenter'] = request.user.profile.id
            serializer = CommentSerializer(data = data, context = {'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response({'msg':"You can't comment twice on same document"},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pass

class VoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_document(self,doc_id):
        try:
            return Document.objects.get(id=doc_id)
        except:
            raise Http404

    def get(self, request, doc_id, *args, **kwargs):
        document = self.get_document(doc_id)
        serializer = DocumentSerializer(document)
        votes = serializer.data.get('stars')
        return Response({'votes':votes},status=status.HTTP_200_OK)

    def doc_upvote(self, doc_id, user, document):
        document.stars += 1
        document.upvoter.add(user)
        document.save()

    def doc_downvote(self, doc_id, user, document):
        document.stars -= 1
        document.downvoter.add(user)
        document.save()

    def post(self,request,doc_id):
        document = self.get_document(doc_id)
        vote = int(request.data.get('vote'))
        user = request.user.profile
        if vote > 0:
            if user in document.upvoter.all():
                return Response({'detail': "Already upvoted"},status=status.HTTP_400_BAD_REQUEST)
            elif user in document.downvoter.all():
                self.doc_upvote(doc_id, user, document)
                document.downvoter.remove(user)
                return Response({'msg':'Document has been upvoted'},status=status.HTTP_200_OK)
            self.doc_upvote(doc_id, user, document)
            return Response({'msg':'Upvoted'},status=status.HTTP_200_OK)
        if user in document.downvoter.all():
                return Response({'detail': "Already downvoted"},status=status.HTTP_400_BAD_REQUEST)
        elif user in document.upvoter.all():
            self.doc_downvote(doc_id, user, document)
            document.upvoter.remove(user)
            return Response({'msg':'Document has been downvoted'},status=status.HTTP_200_OK)
        self.doc_downvote(doc_id, user, document)
        return Response({'msg':'Downvoted'},status=status.HTTP_200_OK)



class CollegeView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        data = College.objects.all()
        serializer = CollegeSerializer(data, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_doc(self,doc_id):
        try:
            return Document.objects.get(id=doc_id)
        except:
            raise Http404

    def post(self, request, doc_id):
        document = self.get_doc(doc_id)
        user  = request.user.profile
        if user not in document.bookmark.all():
            document.bookmark.add(user)
            return Response({'msg': "Bookmark added"},status=status.HTTP_201_CREATED) 
        return Response({'msg': "Post already bookmarked"},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, doc_id):
        document = self.get_doc(doc_id)
        user  = request.user.profile
        print(user)
        print(document.bookmark.all())
        if user in document.bookmark.all():
            document.bookmark.remove(user)
            return Response({'msg': "Bookmark removed"},status=status.HTTP_201_CREATED) 
        return Response({'msg': "Post is not bookmarked"},status=status.HTTP_400_BAD_REQUEST)
    
class GetBookmarks(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(id = user_id)
        except:
            raise Http404

    def get(self, request, user_id):
        user = self.get_user(user_id)
        print(user.doc_bookmarked.all())
        forum = DocumentSerializer(user.doc_bookmarked.all(), many = True, context = {'request':request})
        data = forum.data
        return Response(data, status = status.HTTP_200_OK)



