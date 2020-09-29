from rest_framework import viewsets, generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .permissions import IsLoggedInUserOrAdmin, IsAdminUser

from .models import User, OtpModel, UserProfile
from .serializers import UserSerializer,MyTokenObtainPairSerializer


from django.http import Http404

from random import randint
from django.core.mail import send_mail

from rest_framework_simplejwt.tokens import RefreshToken

import time
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# /////////////////////////////

# For registring a User: UserViewSet.POST(OTP generation + Email) -> OTPVerificationView(Verifies the OTP) 
# For Reseting the password: PasswordResetView -> PasswordResetOTPConfirmView -> UserViewSet.PUT

# /////////////////////////////


# To get custom tokens for a User; To be used in Password Reset
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# View for Users 
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        coming_data = request.data
        request_email = coming_data.get("email", "")
        
        if request_email:
            user = User.objects.filter(email__iexact = request_email)
            
            if user.exists():
                    return Response(status = status.HTTP_226_IM_USED) # "User with this email already exists"

            else:
                    otp = randint(100000, 999999) 
                    time_of_creation = int(time.time())
                    OtpModel.objects.create(otp = otp, otp_email = request_email, time_created = time_of_creation)
                    mail_body = f"Hello Your OTP for registration is {otp}. This OTP will be valid for 5 minutes."
                    send_mail('OTP for registering on SmartLearn', mail_body, 'nidhi.smartlearn@gmail.com', [request_email], fail_silently = False) 
                    serializer = UserSerializer(data = coming_data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status = status.HTTP_201_CREATED)
                    else:
                        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
                    return Response(status = status.HTTP_200_OK)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        if str(request.user) == User.objects.get(pk = pk).email:
            new_password = request.data.get('password', "")
            if new_password:
                user = User.objects.get(pk = pk)
                user.set_password(new_password)
                user.save()
                return Response(status = status.HTTP_202_ACCEPTED)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        return Response(status = status.HTTP_401_UNAUTHORIZED)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedInUserOrAdmin]
        elif self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]




class OTPVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        coming_data = request.data
        print(coming_data)

        request_otp   = coming_data.get("otp","")
        request_email = coming_data.get("email","")
        request_is_teacher = coming_data.get("is_teacher","")
        print(request_is_teacher)
        current_time = int(time.time())

        try:
            query        = OtpModel.objects.get(otp_email__iexact = request_email)
            # print(query)
        except:
            raise Http404

        otpmodel_email      = query.otp_email 
        # print(otpmodel_email)
        otpmodel_otp        = query.otp
        otp_creation_time   = query.time_created

        
        if request_email == otpmodel_email and request_otp == otpmodel_otp and (current_time - otp_creation_time < 300):

            user  =  User.objects.get(email__iexact = request_email)
            user.is_active = True
            user.save()
            print(UserProfile.objects.get(user = user).is_teacher)

            user_profile = UserProfile.objects.get(user = user)
            user_profile.is_teacher = request_is_teacher
            user_profile.save()
            
            
            OtpModel.objects.filter(otp_email__iexact = request_email).delete()


            return Response(status = status.HTTP_202_ACCEPTED)
        
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST)



# Password Reset View
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_email = request.data.get("email","")
        print(request_email)
        # try:
        #     OtpModel.objects.get(otp_email__iexact = request_email)
        #     print("caca")
        # except: 
        #     return Response(status = status.HTTP_400_BAD_REQUEST)

        user_active_status = User.objects.get(email__iexact = request_email).is_active

        if request_email and user_active_status:
            try:
                user = User.objects.get(email__iexact = request_email)
            except:
                raise Http404
            
            otp = randint(100000, 999999) 
            time_of_creation = int(time.time())
            OtpModel.objects.create(otp = otp, otp_email = request_email, time_created = time_of_creation)
            # mail_body = f"Hello Your OTP for registration is {otp}. This OTP will be valid for 5 minutes."
            # send_mail('OTP for registering on SmartLearn', mail_body, 'nidhi.smartlearn@gmail.com', [user_email], fail_silently = False) 
            data = {"id": user.id}
            return Response(data, status = status.HTTP_200_OK)

class PasswordResetOTPConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        coming_data = request.data
        request_otp   = coming_data.get("otp","")
        request_email = coming_data.get("email","")
        if request_email:
            try:
                otpmodel = OtpModel.objects.get(otp_email__iexact = request_email)
                print(otpmodel)
                user = User.objects.get(email__iexact = request_email)
                print(user)
            except:
                raise Http404
                

            
            if otpmodel.otp_email == request_email and otpmodel.otp == request_otp:
                OtpModel.objects.filter(otp_email__iexact = request_email).delete()
                return Response(get_tokens_for_user(user))
            return Response(status = status.HTTP_400_BAD_REQUEST)
        return Response(status = status.HTTP_400_BAD_REQUEST)
            


class OTPResend(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        coming_data = request.data
        request_email = coming_data.get("request_email","")
        try:
            User.objects.get(email__iexact = request_email)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)

        OtpModel.objects.filter(otp_email__iexact = request_email).delete()

        if request_email:
            otp = randint(100000, 999999) 
            time_of_creation = int(time.time())
            OtpModel.objects.create(otp = otp, otp_email = request_email, time_created = time_of_creation)
            # mail_body = f"Hello Your OTP for registration is {otp}. This OTP will be valid for 5 minutes."
            # send_mail('OTP for registering on SmartLearn', mail_body, 'nidhi.smartlearn@gmail.com', [request_email], fail_silently = False) 
