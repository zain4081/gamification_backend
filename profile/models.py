from django.db import models
from django.contrib.auth.models import AbstractUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class CustomUser(TimeStampedModel, AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_pm = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=255, null=True, blank=True)
    is_reset_attempt = models.BooleanField(default=False)