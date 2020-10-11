from rest_framework import viewsets, generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .permissions import IsLoggedInUserOrAdmin, IsAdminUser

from .models import User, OtpModel, UserProfile
from .serializers import UserSerializer,MyTokenObtainPairSerializer, UserProfileSerializer


from django.http import Http404

from random import randint
from django.core.mail import send_mail

from rest_framework_simplejwt.tokens import RefreshToken

import time
from rest_framework_simplejwt.views import TokenObtainPairView

from django.template import loader

from rest_framework import generics



# /////////////////////////////

# For registring a User: UserViewSet.POST(OTP generation + Email) -> OTPVerificationView(Verifies the OTP) 
# For Reseting the password: PasswordResetView -> PasswordResetOTPConfirmView -> UserViewSet.PUT

# /////////////////////////////



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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
        print(coming_data)
        request_email = coming_data.get("email", "")
        
        if request_email:
            user = User.objects.filter(email__iexact = request_email)
            
            if user.exists():
                    return Response("{User with this email already exists}",status = status.HTTP_226_IM_USED) 

            else:
                    send_otp_email(request_email, body = "OTP for registering your Account with SmartLearn")
                    serializer = UserSerializer(data = coming_data,context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                        return Response("OTP has been sent", status = status.HTTP_201_CREATED)
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
                print(user)
                user.set_password(new_password)
                user.save()
                serializer = UserProfileSerializer(user.profile,context={'request': request})
                data = dict()
                data['email']  = user.email
                data['is_teacher'] = user.profile.is_teacher
                data.update(serializer.data)
                mail_body = "You have succesfully changed your password for your SmartLearn account"
                context = {'body':mail_body}
                html_content = loader.render_to_string('msg.html', context)
                send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [user.email], html_message = html_content, fail_silently = False) 
                # send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [user.email], fail_silently = False) 
                return Response(data, status = status.HTTP_202_ACCEPTED)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        return Response(status = status.HTTP_401_UNAUTHORIZED)


    # def put(self, request, pk):
    #     user = User.objects.get(pk = pk)
    #     serializer = UserSerializer(user, data = request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status = status.HTTP_200_OK)
    #     return Response(serializer.errors,status = status.HTTP_401_UNAUTHORIZED)

    # def partial_update(self, request, pk):
    #     if request.user == User.objects.get(pk = pk):

    #         new_password = request.data.get('password', "")
    #         user = User.objects.get(pk = pk)

    #         if not user.check_password(new_password): 
    #             if new_password:
    #                 user.set_password(new_password)
    #                 user.save()
    #                 serializer = UserProfileSerializer(user.profile,context={'request': request})
    #                 data = dict()
    #                 data['email']  = user.email
    #                 data['is_teacher'] = user.profile.is_teacher
    #                 data.update(serializer.data)

    #                 mail_body = "You have succesfully changed your password for your SmartLearn account"
    #                 context = {'body':mail_body}
    #                 html_content = loader.render_to_string('msg.html', context)
                    # send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [user.email], html_message = html_content, fail_silently = False) 

    #                 return Response(data, status = status.HTTP_202_ACCEPTED)
    #             return Response({'detail':'Password must not be null'}, status = status.HTTP_400_BAD_REQUEST)
    #         return Response({'detail':'Password is same as old'},status = status.HTTP_406_NOT_ACCEPTABLE)
    #     return Response({'detail':'User does not exists'},status = status.HTTP_401_UNAUTHORIZED)

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
        except:
            raise Http404

        otpmodel_email      = query.otp_email 
        otpmodel_otp        = query.otp
        otp_creation_time   = query.time_created

        
        if request_email == otpmodel_email and request_otp == otpmodel_otp and (current_time - otp_creation_time < 300):

            user  =  User.objects.get(email__iexact = request_email)
            user.is_active = True
            user.save()

            user_profile = UserProfile.objects.get(user = user)
            user_profile.is_teacher = request_is_teacher
            user_profile.save()
            
            OtpModel.objects.filter(otp_email__iexact = request_email).delete()
            mail_body = "Congratulations..! You have successfully registered and verified your acoount on Smartlearn"
            context = {'body':mail_body}
            html_content = loader.render_to_string('msg.html', context)
            context = {'body':mail_body}
            html_content = loader.render_to_string('msg.html', context)
            # send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [request_email], html_message = html_content, fail_silently = False) 
            return Response(status = status.HTTP_202_ACCEPTED)
        return Response(status = status.HTTP_400_BAD_REQUEST)



# Password Reset View
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        request_email = request.data.get("email","")
        try:
            user = User.objects.get(email__iexact = request_email)
        except: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            send_otp_email(request_email, body = "OTP for verifying your SmartLearn account")
            return Response({"User is registered but not verified. An OTP has been sent to email."}, status = status.HTTP_308_PERMANENT_REDIRECT)

        if request_email:
            send_otp_email(request_email, body = "OTP for resetting your password of your SmartLearn account") 
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
                user = User.objects.get(email__iexact = request_email)
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
        request_email = coming_data.get("email","")
        try:
            User.objects.get(email__iexact = request_email)
        except:
            return Response('{User not found}',status = status.HTTP_400_BAD_REQUEST)

        if request_email:
            send_otp_email(request_email, body = "OTP, that you have requested")
            return Response({"An OTP has been sent to provided Email"}, status = status.HTTP_202_ACCEPTED)



def send_otp_email(email, body):
    OtpModel.objects.filter(otp_email__iexact = email).delete()

    otp = randint(100000, 999999) 
    time_of_creation = int(time.time())
    OtpModel.objects.create(otp = otp, otp_email = email, time_created = time_of_creation)

    context = {
        'otp' : otp,
        'body': body,
    }

    html_content = loader.render_to_string('index.html', context)
    mail_body = f"{body} is {otp}. This OTP will be valid for 5 minutes."
    send_mail('Greetings from SmartLearn Team', mail_body, 'SmartLearn<nidhi.smartlearn@gmail.com>', [email], html_message = html_content, fail_silently = False) 
    return None
