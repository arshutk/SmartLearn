from django.db import models

from userauth.models import UserProfile

from django.core.validators import FileExtensionValidator


class College(models.Model):
    CATEGORY = (
                ('Medical','Medical'),
                ('Engineering','Engineering'),
                ('Law','Law'),
                ('Arts','Arts'),
                ('Business','Business'),
               )

    name        = models.CharField(max_length = 35) 
    scope       = models.CharField(max_length = 35, choices = CATEGORY, default = None)
    
    def __str__(self):
            return self.name 


class Document(models.Model):
    CATEGORY = (
                ('Book','Book'),
                ('Note','Note'),
               )
    title       = models.CharField(max_length = 35)
    description = models.TextField()
    file        = models.FileField(upload_to = 'library/', max_length = 50000000, validators=[FileExtensionValidator(['pdf'])])
    stars       = models.IntegerField(default = 0)
    category    = models.CharField(max_length = 20, choices = CATEGORY, default = 'Misc')
    college     = models.ForeignKey(College, on_delete=models.CASCADE, related_name="college")
    uploader    = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="uploaded_by")
    voter       = models.ManyToManyField(UserProfile,related_name="star_voter", blank = True)
    bookmark    = models.ManyToManyField(UserProfile, related_name="doc_bookmarked", blank = True)

    class Meta:
        ordering = ('-stars',)

    def __str__(self):
        return f"{self.title} : {self.uploader.user.email}"


class Comment(models.Model):
    text        = models.CharField(max_length = 50)
    document    = models.ForeignKey(Document, on_delete = models.CASCADE, related_name = 'doc_comment')
    commenter   = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="commented_by")

    def __str__(self):
            return self.text 