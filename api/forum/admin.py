from django.contrib import admin
from forum.models import Forum, Comment, Label

admin.site.register(Forum)
admin.site.register(Label)
admin.site.register(Comment)