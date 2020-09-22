from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from userauth.models import UserProfile
from .models import Classroom
from .serializers import ClassroomSerializer
from userauth.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from rest_framework.response import Response


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    def create(self, request):
        data = request.data
        user = request.user
        teacher = UserProfile.objects.get(user=user).pk
        data['teacher'] = teacher
        data['student'] = []
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    permission_classes = [AllowAny]
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ClassjoinView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        class_code = request.data["class_code"]
        try:
            class_join = Classroom.objects.get(class_code=class_code)
        except:
            return Response({
                "error" : "No such class.",
                "user" : request.user.email
            },status=status.HTTP_400_BAD_REQUEST
            )
        
        current_user =  UserProfile.objects.get(user=request.user)
        class_join.student.add(current_user)
        class_join.save()
        return Response({'detail': f'{ request.user.email }joined{class_join} succesfully'}, status=status.HTTP_201_CREATED)



