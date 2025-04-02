from django.db import models

# Create your models here.
from datetime import datetime
from datetime import timedelta
from django.contrib.auth import get_user_model
from .choices import EVENT_TYPE
import uuid

from django.urls import reverse
from session_client.models import Client

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
    class Meta:
        verbose_name = "room calendar"
        verbose_name_plural = "room calendars"
        ordering = ("name",)
    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Container model for general metadata and associated ``OccurrenceModel`` entries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    room_calendar = models.ForeignKey(RoomCalendarModel,on_delete=models.SET_NULL,blank=True,null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL,blank=True,null=True)
    title = models.CharField(max_length=32,blank=True)
    description = models.CharField(max_length=100,blank=True)
    event_type = models.CharField(choices=EVENT_TYPE,max_length=20, verbose_name="event type")

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ("updated_at","title")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("room_calendar_app:event", args=[str(self.id)])
    
    @property
    def color_class(self): #to add a color class or other relative to event type
        match self.event_type:
            case 'client':
                return 'primary'
            case 'super':
                return 'secondary'
            case 'admin':
                return 'danger'
            case 'Processing':
                return 'warning'
            case 'CPD':
                return 'info'
        

class OccurrenceManager(models.Manager):
    def create_unique(self,start_time:datetime,duration:datetime,event:Event,room=None):
        """ creates an occurrence and checks if overlaps with others. 
            Returns (True,None) if it does not overlaps, and (False,Queryset) if it does  """
        end_time = start_time + duration
        calendar = room if room else event.room_calendar
        new_occ = self.create(
            start_time=start_time,
            duration=duration,
            end_time=end_time,
            event=event,
            calendar=calendar,
        )
        overlaps = new_occ.overlap_set()
        if overlaps:
            return False,overlaps
        else:
            new_occ.save()
            True,None

class OccurrenceModel(models.Model):
    """ sets an occurrence by having a start and end, and a event attached """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    duration = models.DurationField()
    end_time = models.DateTimeField()
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,null=True)
    objects = OccurrenceManager()
    calendar = models.ForeignKey(RoomCalendarModel,null=True,blank=True,on_delete=models.SET_NULL)

    class Meta:
        verbose_name ="occurrence"
        verbose_name_plural = "occurrences"
        ordering = ("start_time",)
        base_manager_name = "objects"

    def __str__(self):
        return "{}: {}".format(self.event.title, self.start_time.isoformat())

    def get_absolute_url(self):
        return reverse("room_calendar_app:edit_occurrence_list", args=[str(self.event.id), str(self.id)])

    def __lt__(self, other):
        return self.start_time < other.start_time
    
    def repeat_next_week(self,weeks=1):
        start_time = self.start_time + timedelta(weeks=weeks)
        end_time = self.end_time + timedelta(weeks=weeks)
        created,set = self.manager.create_unique(start_time=start_time,
                                  end_time=end_time,
                                  duration=self.duration,
                                  event=self.event,
                                  room_calendar=self.room_calendar
                                  )
        return created

    def overlap_set(self):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.
        """
        start = self.start_time
        end = self.end_time
        qs = OccurrenceModel.objects.filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            )
            | models.Q(
                end_time__gte=start,
                end_time__lte=end,
            )
            | models.Q(start_time__lt=start, end_time__gt=end)
        )
        return qs

    @property
    def event_title(self):
        return self.event.title

    @property
    def room_calendar(self):
        return self.event.room_calendar
    @property
    def week_day(self):
        return self.start_time.day
