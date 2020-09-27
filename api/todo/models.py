from django.db import models
from userauth.models import UserProfile
# Create your models here.
class Todo(models.Model):
    title = models.CharField(max_length=20,blank=False)
    description = models.TextField(max_length=250,blank=True)
    date_time = models.DateTimeField(null=True)
    done = models.BooleanField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="todo")
    def __str__(self):
        return self.title