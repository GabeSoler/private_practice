from django.db import models
from django.contrib.auth import get_user_model
import uuid

# Create your models here.

class TransactionModel(models.Model):
    """a model to organise transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date = models.DateField(blank=True, null=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True,default=60.00)
