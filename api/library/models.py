from django.db import models

from userauth.models import UserProfile

from django.core.validators import FileExtensionValidator

class Document(models.Model):
    CATEGORY = (
                ('Book','Book'),
                ('Note','Note'),
               )
    title       = models.CharField(max_length = 35)
    description = models.TextField()
    file        = models.FileField(upload_to='library/', max_length = 500000, validators=[FileExtensionValidator(['pdf'])])
    stars       = models.PositiveIntegerField(default = 0)
    category    = models.CharField(max_length = 20, choices = CATEGORY, default = 'Misc')
    college     = models.CharField(max_length = 35, default = None)
    uploader    = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="uploaded_by")

    class Meta:
        ordering = ('-stars',)

    def __str__(self):
        return f"{self.title} : {self.uploader.user.email}"



class Comment(models.Model):
    text        = models.CharField(max_length = 50)
    document    = models.ForeignKey(Document, on_delete = models.CASCADE, related_name = 'doc_comment')

    def __str__(self):
            return self.text 