from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import Classroom
from .serializers import ClassroomSerializer
from userauth.permissions import IsLoggedInUserOrAdmin, IsAdminUser
from .permissions import IsTeacher,IsStudent

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [AllowAny]
    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated,IsAdminUser]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]