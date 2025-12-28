from django.db import models
from ppm_app.settings.base import AUTH_USER_MODEL
import uuid
from base.choices import (WEEKDAY_SHORT,
                          AGREEMENT_CHOICES,time_slot_options)
from django.utils.translation import gettext_lazy as _

class RoomCalendarModel(models.Model):
    """ a room calendar model that will hold the events """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="controller")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(default="",max_length=20)
    description = models.CharField(default="",max_length=200)
    percentage = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    class Meta:
        app_label = "room_calendar_app"
        verbose_name = "room calendar"
        verbose_name_plural = "room calendars"
        ordering = ("name",)

    def __str__(self):
        return self.name


class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    display_name = models.CharField(max_length=20)
    description = models.CharField(max_length=200,blank=True)
    calendar = models.ForeignKey(RoomCalendarModel,on_delete=models.SET_NULL,null=True)
    agreement = models.CharField(default="Amount",max_length=10, choices=AGREEMENT_CHOICES)

    class Meta:
        app_label = "room_calendar_app"
        verbose_name = "tenant"
        verbose_name_plural = "tenants"
        ordering = ("name",)
    def __str__(self):
        return self.name

class BlocksModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(TenantModel,on_delete=models.CASCADE,help_text=_("Select a linked tenant"))
    day = models.IntegerField(choices=WEEKDAY_SHORT)
    start_time = models.TimeField(choices=time_slot_options())
    end_time = models.TimeField(choices=time_slot_options())
    monthly_cost = models.IntegerField(default=0,blank=True,help_text=_("Monthly cost for this block"))

    class Meta:
        app_label = "room_calendar_app"
        verbose_name = "block"
        verbose_name_plural = "blocks"
        ordering = ("day","start_time")