from django.conf.urls import url, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from userauth.views import UserViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

