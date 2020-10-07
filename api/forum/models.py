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
    title    = models.CharField(max_length=50,blank=False)
    text     = models.TextField(blank=False)
    image    = models.ImageField(upload_to='forum_posts', null = True, blank = True, max_length = 5000)
    votes    = models.IntegerField(default=0)
    voter    = models.ManyToManyField(UserProfile,related_name="voted")
    bookmark = models.ManyToManyField(UserProfile,related_name="bookmarked")
    author   = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='blog')
    tag      = models.ForeignKey(Label, on_delete = models.SET_NULL, null = True, blank = True ,related_name = 'forums')
    def __str__(self):
        return f"{self.author.user.email} -> {self.title}"
    class Meta:
        ordering = ['-votes',]

class Comment(models.Model):
    text           = models.TextField(blank=False)
    is_parent      = models.BooleanField(default = False)
    forum          = models.ForeignKey(Forum,null = True, blank = True, on_delete=models.CASCADE, related_name='comments')
    author         = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null = True, blank = True,related_name="child_comments")
    def __str__(self):
        return f"{str(self.text)[:50]} -> {self.is_parent}"

