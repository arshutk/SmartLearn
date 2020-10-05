from django.db import models
from userauth.models import User, UserProfile


class Label(models.Model):
    CATEGORY = (
            ('Python','Python'),
            ('Java','Java'),
            ('C++','C++'),
            ('Data Structure','Data Structure'),
            ('Art','Art'),
            ('Science','Science'),
            ('Mathematics','Mathematics'),
            ('Commerce','Commerce'),
    )
    label_name = models.CharField(max_length=20, choices = CATEGORY, default = 'None')

    def __str__(self):
        return self.label_name



class Forum(models.Model):
    title  = models.CharField(max_length=50)
    text   = models.TextField()
    image  = models.ImageField(upload_to='forum_posts', null = True, blank = True, max_length = 5000)
    upvote = models.PositiveIntegerField(default = 0)
    user   = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='poster')
    tag    = models.ForeignKey(Label, on_delete = models.SET_NULL, null = True, blank = True ,related_name = 'tag')

    def __str__(self):
        return f"{self.user.user.email} -> {self.title}"



class Comment(models.Model):
    text           = models.TextField()
    is_parent      = models.BooleanField(default = True)
    forum          = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='forum')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return f"{str(self.text)[:50]} -> {self.is_parent}"

