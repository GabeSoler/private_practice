from django.db import models
from django.contrib.auth import get_user_model
import uuid

from my_numbers.choices import QUARTER_CHOICES, PERIOD_TYPE_CHOICES
from session_client.models import SessionModel


# Create your models here.



class ReportModel(models.Model):
    """a model to organise transactions into reporting
        needed to record how a report was made in the future
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    period_type = models.CharField(choices=PERIOD_TYPE_CHOICES,max_length=15)
    quarter = models.IntegerField(choices=QUARTER_CHOICES,blank=True,null=True)
    period_start = models.DateField()
    period_end = models.DateField()


class TransactionModel(models.Model):
    """a model to organise transactions
        would receive sessions fee data and expenses
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True,default=60.00)
    is_income = models.BooleanField(default=False,blank=True,null=True) # expense if false
    report = models.ManyToManyField(ReportModel) # transactions can be added to reports
    is_recurrent = models.BooleanField(default=False,blank=True,null=True) #to suggest in expenses
    session = models.OneToOneField(SessionModel,on_delete=models.SET_NULL,blank=True,null=True)

