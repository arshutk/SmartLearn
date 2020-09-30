from django.conf.urls import url, include
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from .views import ClassroomViewSet,PortalStudentView,PortalTeacherView, ClassjoinView,AssignmentPost,AssignmentView,AnswerSheetPost,AnswerSheetView,ListOfAnswers, DoubtSectionView

router = routers.DefaultRouter()
router.register(r'classroom', ClassroomViewSet)
# router.register(r'doubt', DoubtSectionViewSet)

urlpatterns = [
    #post request with class_code to join a class, teacher cant join his own class
    path('join/',ClassjoinView.as_view()), 
    #both teacher and student can see list of assignment of that class, only teacher can post an assignment
    path('classroom/<int:pk>/assignment/',AssignmentPost.as_view()), 
    #both teacher and student can see the details of a particular assignment
    path('classroom/<int:pk>/assignment/<int:id>/',AssignmentView.as_view()),
    # student can post answer of a paticular assignment in class.
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answer/',AnswerSheetPost.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answer/<int:answer_id>/',AnswerSheetView.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answers/',ListOfAnswers.as_view()),
    # Doubt Section
    path('classroom/<int:class_id>/doubt/',DoubtSectionView.as_view()),
    # Portal
    path('classroom/<int:class_id>/portal/<int:student_id>/',PortalStudentView.as_view()),
    path('classroom/<int:class_id>/portal/teacher/',PortalTeacherView.as_view())
]

urlpatterns += [path('', include(router.urls)),]
