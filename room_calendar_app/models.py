from django.db import models
from django.contrib.auth import get_user_model
import uuid

from room_calendar_app.choices import AGREEMENT_CHOICES
from session_client.choices import duration_times_as_choices, WEEKDAY_SHORT, time_slot_options


class RoomCalendarModel(models.Model):
    """ a room calendar model that will hold the events """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name="controller")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(default="",max_length=20)
    description = models.CharField(default="",max_length=200)
    percentage = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    class Meta:
        verbose_name = "room calendar"
        verbose_name_plural = "room calendars"
        ordering = ("name",)

    def __str__(self):
        return self.name


class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    display_name = models.CharField(max_length=20)
    description = models.CharField(max_length=200,blank=True)
    calendar = models.ForeignKey(RoomCalendarModel,on_delete=models.SET_NULL,null=True)
    agreement = models.CharField(default="Amount",max_length=10, choices=AGREEMENT_CHOICES)

    class Meta:
        verbose_name = "tenant"
        verbose_name_plural = "tenants"
        ordering = ("name",)
    def __str__(self):
        return self.name

class BlocksModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(TenantModel,on_delete=models.CASCADE)
    day = models.IntegerField(choices=WEEKDAY_SHORT)
    start_time = models.TimeField(choices=time_slot_options())
    end_time = models.TimeField(choices=time_slot_options())
    monthly_cost = models.IntegerField(default=0,blank=True,help_text="Monthly cost for this block")