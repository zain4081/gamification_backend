from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Requirement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
