from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    username     = models.CharField(blank=True, null=True, max_length = 30)
    first_name   = models.CharField(blank=True, null=True, max_length = 30)
    last_name    = models.CharField(blank=True, null=True, max_length = 30)
    email        = models.EmailField('email address', unique=True)

    is_active    = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
        

class UserProfile(models.Model):
    user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name ='profile')
    name         = models.CharField(max_length = 30)
    picture      = models.ImageField(upload_to = 'images/', blank = True, null = True, max_length = 1500)

    def __str__(self):
        return self.user.email
        

class OtpModel(models.Model):
    otp          = models.CharField(max_length = 6)
    otp_email    = models.EmailField()
    time_created = models.IntegerField()

    def __str__(self):
        return f"{self.otp_email} : {self.otp}"