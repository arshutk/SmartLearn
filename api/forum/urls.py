from django.conf.urls import url,include
from django.urls import path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from forum import views
router = routers.DefaultRouter()
router.register(r'',views.ForumView)
urlpatterns = [
    path('<int:blog>/comment/',views.CommentView.as_view()),
    path('<int:blog>/comment/<int:comment_id>/',views.CommentOnComment.as_view()),
    path('<int:forum_id>/upvote/',views.UpvoteView.as_view())
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += [path('', include(router.urls)),]