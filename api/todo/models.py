from django.db import models
from userauth.models import UserProfile
from django.db.models import F
# Create your models here.
class Todo(models.Model):
    title = models.CharField(max_length=20,blank=False)
    description = models.TextField(max_length=250,blank=True, null = True)
    date_time = models.DateTimeField(null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="todo")
    def __str__(self):
        return self.title
    class Meta:
        ordering = [F('date_time').asc(nulls_last=True)]