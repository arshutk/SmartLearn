from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from library import views


urlpatterns = [
    path('',views.DocumentView.as_view()),
    path('<int:doc_id>/comment/',views.CommentView.as_view()),
    path('<int:doc_id>/',views.VoteView.as_view()),
    path('<int:doc_id>/bookmark/',views.BookmarkView.as_view()),
    path('bookmark/<int:user_id>/',views.GetBookmarks.as_view()),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
