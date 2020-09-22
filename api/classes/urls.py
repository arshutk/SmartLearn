from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from .views import ClassroomViewSet,ClassjoinView


router = routers.DefaultRouter()
router.register(r'classroom', ClassroomViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'join',ClassjoinView.as_view())
] 
