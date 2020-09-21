from django.conf.urls import url
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from userauth.views import UserViewSet
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

