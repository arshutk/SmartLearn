from django.db import models
from userauth.models import UserProfile

class Classroom(models.Model):
    
    class_code = models.CharField(max_length=50,blank=False,unique=True)
    subject_name = models.CharField(max_length=50,blank=False)
  
    description = models.TextField(max_length=300,blank=True)
   
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE,verbose_name="Teacher",related_name ='teacher')
    student = models.ManyToManyField(UserProfile,verbose_name="Student",related_name ='student',blank=True)
    
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


# {
#     "doubt_text":"helpppp...!",
#     "classroom": "1",
#     "user": "1"
# }
# {
#     "id": 2,
#     "time_created": "2020-09-25T09:41:44.081244Z",
#     "doubt_text": "helpppp...!",
#     "file": null,
#     "classroom": 1,
#     "user": 2
# }

# >>> from classes.models import DoubtSection
# >>> query = DoubtSection.objects
# >>> query.all()
# <QuerySet [<DoubtSection: Anon : Plizz Help...!>, <DoubtSection: Teacher : Plizz Help...!>, <DoubtSection: Student : Plizz Help...!>]>
# >>> query.filter(classroom=1) 
# <QuerySet [<DoubtSection: Anon : Plizz Help...!>, <DoubtSection: Teacher : Plizz Help...!>, <DoubtSection: Student : Plizz Help...!>]>
# >>> query.filter(classroom=2) 
# <QuerySet []>
# >>> query.doubt_text         
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# AttributeError: 'Manager' object has no attribute 'doubt_text'
# >>> query.all().doubt_text 
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# AttributeError: 'QuerySet' object has no attribute 'doubt_text'
# >>> query.get(id=1).doubt_text 
# 'Plizz Help...!'
# >>> query.filter(id=1)        
# <QuerySet [<DoubtSection: Anon : Plizz Help...!>]>
# >>> query.get(id=1)
# <DoubtSection: Anon : Plizz Help...!>
# >>> query.get(id=1).classroom
# <Classroom: qwerty : KAS : Teacher>
# >>> query.get(id=1).classroom.teacher
# <UserProfile: Teacher>
# >>> query.get(id=1).classroom.teacher.name
# 'Teacher'
# >>> query.get(id=1).classroom.student
# <django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x04A5F730>
# >>> query.get(id=1).classroom.student.all()
# <QuerySet [<UserProfile: Student>]>
# >>> query.get(id=1).classroom.student.all()