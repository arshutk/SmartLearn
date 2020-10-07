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
    path('<int:forum_id>/vote/',views.VoteView.as_view()),
    path('<int:forum_id>/bookmark/',views.BookmarkView.as_view()),
    path('bookmark/<int:user_id>/',views.GetBookmarks.as_view()),
    path('post/<str:search>/',views.FilterView.as_view()),
    path('share/<int:post_id>/',views.SharePostView.as_view()),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += [path('', include(router.urls)),]