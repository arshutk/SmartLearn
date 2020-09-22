from django.db import models
from userauth.models import UserProfile
class Classroom(models.Model):
    class_code = models.CharField(max_length=50,blank=False,unique=True)
    subject_name = models.CharField(max_length=50,blank=False)
    subject_code = models.CharField(max_length=10,blank=True)
    description = models.TextField(max_length=300,blank=True)
    standard = models.CharField(max_length=10,blank=False)
    branch = models.CharField(max_length=50,blank=True)
    section = models.CharField(max_length=5,default='1')
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE,verbose_name="Teacher",related_name ='Teacher')
    student = models.ManyToManyField(UserProfile,verbose_name="Student",related_name ='Student')

