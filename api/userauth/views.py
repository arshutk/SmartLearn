from rest_framework import viewsets, generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .permissions import IsLoggedInUserOrAdmin, IsAdminUser


from .models import User, OtpModel
from .serializers import UserSerializer

from random import randint
from django.core.mail import send_mail


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    
class OtpCreation(APIView):
    def post(self, request):
        user_email = request.data.get("email", "")
        if user_email:
            user = User.objects.filter(email__iexact = user_email)
            
            if user.exists():
                    return Response(status = None) # "User with this email already exists"
            else:
                    otp = randint(100000, 999999) 
                    OtpModel.objects.create(otp = otp, otp_email = user_email)
                    mail_body = f"Hello Your OTP for registration is {otp}"
                    send_mail('OTP for registering on SmartLearn', mail_body, 'nidhi.smartlearn@gmail.com', [user_email], fail_silently = False) # OTP send krni h, string nahi
                    return Response(status = status.HTTP_200_OK)
        
        else:
            return Response(status = None) # "User must provide an email"