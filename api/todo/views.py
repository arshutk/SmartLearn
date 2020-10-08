from django.shortcuts import render
from rest_framework import viewsets,status,generics
from rest_framework.response import Response
from .models import Todo
from .serializers import TodoSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from userauth.models import UserProfile

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes =[IsAuthenticated]

    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user.profile)
        return queryset

    def create(self, request):
        data = request.data
        data['user'] = request.user.profile.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
