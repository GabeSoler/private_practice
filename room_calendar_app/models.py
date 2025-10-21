from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
import uuid


class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200,blank=True)
    class Meta:
        verbose_name = "tenant"
        verbose_name_plural = "tenants"
        ordering = ("name",)
    def __str__(self):
        return self.name

class RoomCalendarModel(models.Model):
    """ a room calendar model that will hold the events """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name="controller")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(default="",max_length=20)
    description = models.CharField(default="",max_length=200)
    tenants = models.ManyToManyField(TenantModel,related_query_name="tenants")
    percentage = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    class Meta:
        verbose_name = "room calendar"
        verbose_name_plural = "room calendars"
        ordering = ("name",)
    def __str__(self):
        return self.name

