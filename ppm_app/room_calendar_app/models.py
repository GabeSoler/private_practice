from django.db import models

# Create your models here.
from datetime import datetime
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q
from .choices import EVENT_TYPE
import uuid

from django.urls import reverse
from tools.models import Client

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
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=100)
    event_type = models.CharField(choices=EVENT_TYPE,max_length=20, verbose_name="event type")

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ("updated_at","title")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("swingtime-event", args=[str(self.id)])

    def upcoming_occurrences(self):
        return self.occurrence_set.filter(start_time__gte=datetime.now())
    
    def next_occurrence(self):
        """ return next occurrence """
        upcoming = self.upcoming_occurrences()
        return upcoming[0] if upcoming else None

    def daily_occurrences(self, dt=None):
        """ returns a day occurrences """
        return OccurrenceModel.objects.daily_occurrences(dt=dt, event=self)
    
    @property
    def color_class(self):
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
    def daily_occurrences(self, dt=None, event=None):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.

        ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

         ``event`` can be an ``Event`` instance for further filtering.
        """
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.filter(
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

        return qs.filter(event=event) if event else qs
    
    def is_overlapping_multiple(self,multiple_model):
        """checks if an multiple occurrence call overlaps with current occurrences"""
        start = multiple_model.multiple_start_date
        end = multiple_model.multiple_end_date
        search = self.filter(
                start_time__gte=start,
                end_time__lte=end,)
        return True if search else False



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
        return reverse("swingtime-occurrence", args=[str(self.event.id), str(self.id)])

    def __lt__(self, other):
        return self.start_time < other.start_time
    
    def repeat_next_week(self,weeks=1):
        start_time = self.start_time + timedelta(weeks=weeks)
        duration = self.duration + timedelta(weeks=weeks)
        self.objects.create(start_time=start_time,duration=duration,event=self.event)

    def is_overlapping(self):
        """checks if an instance overlaps with another"""
        start = self.start_time
        duration = self.duration
        end = start + timedelta.min(self.duration)
        search = self.objects.filter(
                Q(start_time__gte=start,start_time__lte=end) and
                Q(duration__lte=duration)
        )
        return True if search else False


    @property
    def title(self):
        return self.event.title

    @property
    def room_calendar(self):
        return self.event.room_calendar
    @property
    def day(self):
        return self.start_time.day
