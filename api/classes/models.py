from django.db import models
from userauth.models import UserProfile

class Classroom(models.Model):
    
    class_code = models.CharField(max_length=50,blank=False,unique=True)
    subject_name = models.CharField(max_length=50,blank=False)
    description = models.TextField(max_length=300,blank=True)   
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE,verbose_name="Teacher",related_name ='ClassTeacher')
    student = models.ManyToManyField(UserProfile,verbose_name="Student",related_name ='ClassStudent',blank=True)
    def __str__(self):
        return f'{self.class_code} -> {self.subject_name} -> {self.teacher}'

class Assignment(models.Model):
    
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=True)
    submit_by = models.DateTimeField(blank=True,null=True)
    max_marks = models.DecimalField(max_digits=5,decimal_places=1,default=100)
    file_linked = models.FileField(upload_to='class/assignment',blank = True, null = True, max_length = 1500000)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,related_name='assignment')
    def __str__(self):
        return self.title

        
class AnswerSheet(models.Model):
    
    file_linked = models.FileField(upload_to="class/answers", blank=True, max_length= 1500000)
    marks_scored = models.DecimalField(max_digits=5,decimal_places=1,default=0)
    late_submitted = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='answersheet')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='answersheet')
    def __str__(self):
        return f'{self.student} - {self.assignment}'


class DoubtSection(models.Model):
    
    time_created = models.DateTimeField(auto_now_add = True)
    doubt_text = models.TextField(max_length = 300)
    file = models.FileField(upload_to = 'doubt-pdf/', blank = True, null = True, max_length = 1500)

    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE, verbose_name = "Classroom", related_name = "doubt")
    user      = models.ForeignKey(UserProfile, on_delete=models.CASCADE,  verbose_name = "UserProfile", related_name = "userprofile")

    def __str__(self):
        return f'{self.user} : {str(self.doubt_text)[:50]}'