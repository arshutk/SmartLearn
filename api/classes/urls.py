from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from .views import ClassroomViewSet,ClassjoinView, DoubtSectionList, DoubtSectionDetail
# ,ClassList


router = routers.DefaultRouter()
router.register(r'classroom', ClassroomViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'join', ClassjoinView.as_view()),

    path(r'doubtsection/', DoubtSectionList.as_view()),
    path(r'doubtsection/<int:pk>/', DoubtSectionDetail.as_view()),
] 
