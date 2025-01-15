from django.db import models
from django.contrib.auth import get_user_model
from profile.models import TimeStampedModel
from ckeditor.fields import RichTextField

User = get_user_model()

class Project(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = RichTextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_manager')
    users = models.ManyToManyField(User, related_name='project_users')

    def __str__(self):
        return self.name

class Requirement(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
