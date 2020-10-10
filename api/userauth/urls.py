from django.conf.urls import url
from django.urls import path,include

from rest_framework import routers
# from userauth.views import UserViewSet, OTPVerificationView, PasswordResetView, PasswordResetOTPConfirmView,MyTokenObtainPairView, OTPResend, 
# UserUpdateProfile
from userauth import views

from rest_framework_simplejwt import views as jwt_views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    url(r'^', include(router.urls)),
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', views.OTPVerificationView.as_view()),
    # path('update/', UserUpdateProfile.as_view()),
    path('password/reset', views.PasswordResetView.as_view()),
    path('password/reset/verify', views.PasswordResetOTPConfirmView.as_view()),
    path('otp/resend/', views.OTPResend.as_view()),
    path('class/',include('classes.urls')),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
# ] 

