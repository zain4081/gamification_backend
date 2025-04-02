from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Roles(TimeStampedModel):
    name= models.CharField(max_length=255, unique=True)

class CustomUser(TimeStampedModel, AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_pm = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=255, null=True, blank=True)
    is_reset_attempt = models.BooleanField(default=False)
    roles = models.ForeignKey(Roles, on_delete=models.CASCADE)
    points = models.PositiveBigIntegerField(default=0)

