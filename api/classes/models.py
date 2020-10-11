from django.db import models
from userauth.models import UserProfile
from .validators import validate_file_extension
from django.db.models import Q
class Classroom(models.Model):
    class_code = models.CharField(max_length=50,blank=False,unique=True)
    subject_name = models.CharField(max_length=50,blank=False)
    description = models.TextField(max_length=300,blank=True)   
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE,verbose_name="Teacher",related_name ='ClassTeacher')
    student = models.ManyToManyField(UserProfile,verbose_name="Student",related_name ='ClassStudent',blank=True)
    def __str__(self):
        return f'{self.class_code} -> {self.subject_name} -> {self.teacher}'
    class Meta:
        ordering = ('-id',)

class Assignment(models.Model):
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now=True)
    submit_by = models.DateTimeField(blank=True,null=True)
    max_marks = models.PositiveIntegerField(default=100)
    file_linked = models.FileField(upload_to='class/assignment', null = True, max_length = 1500000,validators=[validate_file_extension])
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,related_name='assignment')
    def __str__(self):
        return self.title
    class Meta:
        unique_together = ("title", "classroom")
        ordering = ('-time_created',)


class AnswerSheet(models.Model):
    file_linked = models.FileField(upload_to="class/answers", null=True, max_length= 1500000,validators=[validate_file_extension])
    marks_scored = models.PositiveIntegerField(default=0)
    late_submitted = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='answersheet')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='answersheet')
    def __str__(self):
        return f'{self.student} - {self.assignment}'


class DoubtSection(models.Model):
    time_created= models.DateTimeField(auto_now_add = True)
    doubt_text  = models.TextField(max_length = 800)
    file        = models.FileField(upload_to = 'doubt-pdf/', blank = True, null = True, max_length = 1500000,validators=[validate_file_extension])
    classroom   = models.ForeignKey(Classroom, on_delete = models.CASCADE, verbose_name = "Classroom", related_name = "doubt")
    user        = models.ForeignKey(UserProfile, on_delete=models.CASCADE,  verbose_name = "UserProfile", related_name = "userprofile")

    def __str__(self):
        return f'{self.user} : {str(self.doubt_text)[:50]}'
    
    class Meta:
        ordering = ('-time_created',)

class PrivateChat(models.Model):
    time_created = models.DateTimeField(auto_now_add = True)
    text         = models.TextField(max_length = 500)
    file         = models.FileField(upload_to='privatechat/', null = True, blank = True, max_length = 500000, validators=[validate_file_extension])
    sender       = models.ForeignKey(UserProfile, on_delete = models.CASCADE, related_name = "senderprofile" )
    reciever     = models.ForeignKey(UserProfile, on_delete = models.CASCADE, related_name = "recieverprofile")
    classroom    = models.ForeignKey(Classroom,   on_delete = models.CASCADE, related_name = "chatprivate")

    def __str__(self):
        return f'{self.sender.user.email} --> {self.reciever.user.email}'
    
    class Meta:
        ordering = ('-time_created',)

class PrivateComment(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=300)
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name="private_chats")
    sender = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="private_chat_sent")
    receiver = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="private_chat_received")
    def ___str__(self):
        return f'{self.author.name} - {self.time_created}'
    class Meta:
        ordering = ['time_created']

class Quiz(models.Model):
    name = models.CharField(max_length=1000)
    questions_count = models.IntegerField(default=0)
    description = models.CharField(max_length=70,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE,related_name="quiz")
    shared = models.BooleanField(default=False)
    class Meta:
        ordering = ["created",]
    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='questions')
    label = models.CharField(max_length=1000)
    order = models.IntegerField(default=0)
    def __str__(self):
        return self.label

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name='answers')
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return self.text

class QuizTakers(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='quiz_taken')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='submitted_by')
    correct_answers = models.IntegerField(default=0)
    # completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.student.name
