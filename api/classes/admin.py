from django.contrib import admin
from .models import Classroom,Assignment,AnswerSheet, DoubtSection


admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(AnswerSheet)
admin.site.register(DoubtSection)
