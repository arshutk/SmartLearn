from django.conf.urls import url, include
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from .views import ClassroomViewSet,ClassjoinView,AssignmentPost,AnswerSheetViewSet,AssignmentView,AnswerSheetPost

router = routers.DefaultRouter()
router.register(r'classroom', ClassroomViewSet)

router.register(r'answer',AnswerSheetViewSet)
urlpatterns = [
    
    path('join',ClassjoinView.as_view()),
    path('classroom/<int:pk>/assignment/',AssignmentPost.as_view()),
    path('classroom/<int:pk>/assignment/<int:id>/',AssignmentView.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answer/',AnswerSheetPost.as_view()),
]
# urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += [path('', include(router.urls)),]