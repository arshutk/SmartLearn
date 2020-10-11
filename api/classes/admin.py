from django.contrib import admin
from . import models


admin.site.register(models.Classroom)
admin.site.register(models.Assignment)
admin.site.register(models.AnswerSheet)
admin.site.register(models.DoubtSection)
admin.site.register(models.PrivateChat)
admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.QuizTakers)
