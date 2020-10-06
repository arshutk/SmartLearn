from django.conf.urls import url, include
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers
from . import views
#from .views import ClassroomViewSet,PortalView, DoubtSectionView,ClassjoinView,AssignmentPost,AssignmentView,AnswerSheetPost,AnswerSheetView,ListOfAnswers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'classroom', views.ClassroomViewSet)

urlpatterns = [
    #post request with class_code to join a class, teacher cant join his own class
    path('join/',views.ClassjoinView.as_view()), 
    #both teacher and student can see list of assignment of that class, only teacher can post an assignment
    path('classroom/<int:pk>/assignment/',views.AssignmentPost.as_view()), 
    #both teacher and student can see the details of a particular assignment
    path('classroom/<int:pk>/assignment/<int:id>/',views.AssignmentView.as_view()),
    # student can post answer of a paticular assignment in class.
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answer/',views.AnswerSheetPost.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answer/<int:answer_id>/',views.AnswerSheetView.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/answers/',views.ListOfAnswers.as_view()),
    path('classroom/<int:class_id>/portal/',views.PortalStudentView.as_view()),
    path('classroom/<int:class_id>/doubt/',views.DoubtSectionView.as_view()),
    path('classroom/<int:class_id>/details/',views.ClassroomDataView.as_view()),
    path('classroom/<int:class_id>/portal/teacher/',views.PortalTeacherView.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/comment/',views.StudentPrivateCommentOnAssignment.as_view()),
    path('classroom/<int:class_id>/assignment/<int:assignment_id>/comment/<int:student_id>/',views.TeacherPrivateCommentOnAssignment.as_view())
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += [path('', include(router.urls)),]
