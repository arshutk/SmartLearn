from library.serializer import DocumentSerializer, CommentSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404

from rest_framework.permissions import AllowAny,IsAuthenticated,IsAuthenticatedOrReadOnly

from library.serializer import DocumentSerializer, CommentSerializer
from library.models import Document, Comment

from userauth.models import UserProfile

class DocumentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        data = Document.objects.all()
        serializer = DocumentSerializer(data, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
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

    def post(self,request,doc_id):
        document = self.get_document(doc_id)
        vote = int(request.data.get('vote'))
        if request.user.profile in document.voter.all():
                return Response({'detail': "Already voted"},status=status.HTTP_400_BAD_REQUEST)
        if vote > 0:
            document.stars += 1
            document.voter.add(request.user.profile)
            document.save()
            return Response(status=status.HTTP_200_OK)
        document.stars -= 1
        document.voter.add(request.user.profile)
        document.save()
        return Response(status=status.HTTP_200_OK)


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

class FilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, query):
        try:
            print(type(query))
            result      = Document.objects.filter(category = query)
            serializer  = DocumentSerializer(result, many = True, context = {'request': request})
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({"There is no document within searched category"},status = status.HTTP_204_NO_CONTENT)