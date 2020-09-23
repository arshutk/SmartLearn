from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    username = models.CharField(blank=True, null=True, max_length = 30)
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
        
  
class UserProfile(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name ='profile')
    name        = models.CharField(max_length = 30)
    picture     = models.ImageField(upload_to = 'images/', blank = True, null = True, max_length = 500)
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.user.email}'
        
      
    
  