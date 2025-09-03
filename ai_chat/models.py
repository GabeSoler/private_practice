from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class OpenAIUser(models.Model):
    """ to link threads with our users """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    thread_id = models.CharField(max_length=100,unique=True)