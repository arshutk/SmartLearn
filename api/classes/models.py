from django.db import models
from userauth.models import UserProfile

class Classroom(models.Model):
    
    class_code = models.CharField(max_length=50,blank=False,unique=True)
    subject_name = models.CharField(max_length=50,blank=False)
  
    description = models.TextField(max_length=300,blank=True)
   
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE,verbose_name="Teacher",related_name ='Teacher')
    student = models.ManyToManyField(UserProfile,verbose_name="Student",related_name ='Student',blank=True)
    
    def __str__(self):
        return f'{self.class_code} : {self.subject_name} : {self.teacher}'





class DoubtSection(models.Model):

    time_created = models.DateTimeField(auto_now_add = True)
    doubt_text = models.TextField(max_length = 300)
    file = models.FileField(upload_to = 'doubt-pdf/', blank = True, null = True, max_length = 1500)

    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE, verbose_name = "Classroom", related_name = "classroom")
    user      = models.ForeignKey(UserProfile, on_delete=models.CASCADE,  verbose_name = "UserProfile", related_name = "userprofile")

    def __str__(self):
        return f'{self.user} : {str(self.doubt_text)[:50]}'