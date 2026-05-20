from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class CustomUser(AbstractUser):
    pass

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


REASONS = [
    ("no_inter", "No interested"),
    ("no_use", "Interested but not using it"),
    ("no_reason", "No reasons"),
    ("privacy", "Worried for my privacy"),
    ("no_fit", "Style does not fit me"),
]


class DeleteAccount(models.Model):
    """leave trace of deleted accounts"""
    reason = models.CharField(max_length=20, choices=REASONS, default='')
    confirm = models.BooleanField()
