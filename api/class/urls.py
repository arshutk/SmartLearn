from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from .views import ClassroomViewSet


router = routers.DefaultRouter()
router.register(r'classroom', ClassroomViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
] 
