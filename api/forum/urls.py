from django.conf.urls import url
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from forum import views

urlpatterns = [
    

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
