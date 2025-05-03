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
    code = models.CharField(blank=False,max_length=10,help_text="Add an Identifier code") #Create a code instead of name
    nick_name = models.CharField(default="",blank=True,null=True,max_length=20,help_text="Give it a memorable nickname")
    type = models.CharField(default='Pvt',choices=(CLIENT_TYPE),max_length=20,help_text="Select a type of client") # add choices like private, service, eap, supervisee
    fee = models.IntegerField(default=50,validators=(MinValueValidator(1),MaxValueValidator(100)),help_text="Whats your agreed fee")
    #client base info(delete after 7 yeas?)(I am thinking to only erase the fields as the admin is yours)
    active = models.BooleanField(default=True,help_text="Change if your client is active or archived")
    archived_at = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f"{self.code}"
    
    def get_absolute_url(self):
        return reverse("session_client:client", kwargs={"client_pk":self.pk})
    
class Session(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.PROTECT,help_text="Link to a client")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    session_date = models.DateTimeField(null=True,blank=True, editable=True,help_text="When was the session?")
    #Session labels(delete after 7 years?)
    title = models.CharField(default='',max_length=200,help_text="Give the session a title") #short description
    notes = models.TextField(default='',blank=True,help_text="Longer note of Session") #longer description
    #admin info
    paid = models.BooleanField(default=False,blank=True) #check payment
    attended = models.CharField(default='',blank=True,max_length=20,choices=(ATTENDANCE)) #record attendance
    amount_paid = models.IntegerField(default=0,blank=True) #record attendance
    open = models.BooleanField(default=True,blank=True)
    def __str__(self):
        title = self.title
        return f"Session-{title[:10]}"
    
    def get_absolute_url(self):
        return reverse("session_client:session", kwargs={"session_pk":self.id})
  