from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
from django.urls import reverse
from .choices import ATTENDANCE,CLIENT_TYPE
# Create your models here.

class Client(models.Model):
    """a model to organise clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    #Client labels
    code = models.CharField(default='',max_length=10) #Create a code instead of name
    nick_name = models.CharField(default="",blank=True,null=True,max_length=20)
    type = models.CharField(default='Pvt',choices=(CLIENT_TYPE),max_length=20) # add choices like private, service, eap, supervisee
    fee = models.IntegerField(default=50,validators=(MinValueValidator(1),MaxValueValidator(100)))
    #client base info(delete after 7 yeas?)(I am thinking to only erase the fields as the admin is yours)
    motive = models.CharField(default='',max_length=200) # what broght them
    rel = models.TextField(default='') # for a relationship description
    goal = models.TextField(default='') # Things you agree to work
    strategy = models.TextField(default='') # what you are thinking you could do
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"
    
    def get_absolute_url(self):
        return reverse("tools:client", kwargs={"client_pk":self.pk})
    
class Session(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.PROTECT)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    #Session labels(delete after 7 years?)
    title = models.CharField(default='Session',max_length=200) #short description
    notes = models.TextField(default='') #longher description
    #admin info
    paid = models.BooleanField(default=False) #check payment
    attended = models.CharField(default='attended',max_length=20,choices=(ATTENDANCE)) #record attendance
    amount_paid = models.IntegerField(default=0,blank=True,null=True) #record attendance

    def __str__(self):
        date = self.created_at.strftime("%m/%d/%Y")
        return f"Session: {date}"
    
    def get_absolute_url(self):
        return reverse("tools:session", kwargs={"session_pk":self.id})
  