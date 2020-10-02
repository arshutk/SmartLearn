from django.conf.urls import url
from django.urls import path,include

from rest_framework import routers
from userauth.views import UserViewSet, OTPVerificationView, PasswordResetView, PasswordResetOTPConfirmView,MyTokenObtainPairView, OTPResend

from rest_framework_simplejwt import views as jwt_views


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', OTPVerificationView.as_view()),
    path('password/reset', PasswordResetView.as_view()),
    path('password/reset/verify', PasswordResetOTPConfirmView.as_view()),
    path('otp/resend/', OTPResend.as_view()),
    path('class/',include('classes.urls')),
] 

