from django.db import models

# Create your models here.
from datetime import datetime
from dateutil import rrule
from datetime import datetime, date, time, timedelta
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Q
from .choices import FREQUENCY_CHOICES, ON_EACH, ORDINAL, WEEKDAY_LONG, WEEKDAY_SHORT, ISO_WEEKDAYS_MAP, EVENT_TYPE, time_slots,default_timeslot_options
import uuid

from django.db import models
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

    room_calendar = models.ForeignKey(RoomCalendarModel,on_delete=models.PROTECT,blank=True,null=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT,blank=True,null=True)
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
    
    def add_single_occurrence(self, start_time, end_time):
        """adds one occurrence of this event"""
        self.occurrence_set.create(start_time=start_time, end_time=end_time)


class MultiOccurrenceModel(models.Model):
    """ Model that holds the multiple occurrences setting of an Event """
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    day_start = models.DateField()
    start_time = models.IntegerField(choices=default_timeslot_options)
    end_time = models.IntegerField(choices=default_timeslot_options)
    # recurrence options
    until = models.DateField(default=date.today,blank=True)
    frequency = models.IntegerField(default=rrule.WEEKLY,choices=FREQUENCY_CHOICES)
    interval = models.IntegerField(blank=True,default=1)
    # weekly options
    week_days_1 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    week_days_2 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    week_days_3 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    # monthly options
    month_option = models.CharField(choices=ON_EACH,default="each",max_length=20)
    month_ordinal = models.IntegerField(choices=ORDINAL,blank=True) # which week of month
    month_ordinal_day = models.IntegerField(choices=WEEKDAY_LONG,blank=True) #which day of that week
    each_month_day = models.IntegerField(default=1,blank=True)

    def _build_rrule_params(self):
        iso = ISO_WEEKDAYS_MAP
        params = {"frequency":self.frequency,
                  "interval":self.interval,
                  "until":self.until,
                  "byweekday":None,
                  "bysetpos":None,
                  "bymonthday":self.each_month_day,
                  }

        if self.frequency == rrule.WEEKLY:
            params["byweekday"] = (self.week_days_1,self.week_days_2,self.week_days_3)
        elif self.frequency == rrule.MONTHLY:
            if self.month_option == "on":
                ordinal = self.month_ordinal
                day = iso[self.month_ordinal_day]
                params.update(byweekday=day, bysetpos=ordinal)
            else:
                params["bymonthday"] = self.each_month_day

        elif self.frequency != rrule.DAILY:
            raise NotImplementedError(_("Unknown interval rule " + self.frequency))
        return params
    
    def is_day_week_overlap(self,slot_starts,slot_ends,week_day)->bool:
        """ checks if there is overlap over a day of the week and recurrences forward on the same day and time slot"""
        search = OccurrenceModel.objects.filter(start_time__week_day=week_day).filter(Q(start_time__time__gte=slot_starts) and Q(end_time__time__lte=slot_ends))
        if search:
            return True
        else:
            return False
    def is_day_month_overlap(self,slot_starts,slot_ends,month_day)->bool:
        search = OccurrenceModel.objects.filter(start_time__day=month_day).filter(Q(start_time__time__gte=slot_starts) and Q(end_time__time__lte=slot_ends))
        if search:
            return True
        else:
            return False
    def is_day_week_month_overlap(self,slot_starts,slot_ends,week_day,week_number)->bool: #todo figure out how to set week numbers in a month
        search = OccurrenceModel.objects.filter(
            Q(start_time__gte=datetime.now()) and 
            Q(start_time__week_day=week_day) and 
            Q(start_time__time__gte=slot_starts) and 
            Q(end_time__time__lte=slot_ends))
        if search:
            return True
        else:
            return False
        
    def add_occurrences(self):
        """
        adds multiple occurrences of this event
        """
        rrule_params = self._build_rrule_params()
        until = rrule_params.get("until")
        event = self.event
        start_time = time(self.start_time)
        end_time = self.end_time
        if until:
            rrule_params.setdefault("freq", rrule.DAILY)
            event_duration = end_time - start_time
            occurrences = []
            for date_instance in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(
                    OccurrenceModel(start_time=date_instance, end_time=date_instance + event_duration, event=event)
                )
            self.occurrence_set.bulk_create(occurrences)
        else:
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
    
    def upcoming(self):
        """Return all occurrences of an linked event that are set to start on or after the current
        time."""
        event = self.event
        return event.occurrence_set.filter(start_time__gte=datetime.now())

    def clean_upcoming(self):
        self.upcoming().delete()
    @property
    def multiple_start_date(self):
        day = self.day_start
        start = self.start_time
        compose_start_date = datetime(day=day,time=start)
        return compose_start_date
    @property
    def multiple_end_date(self):
        day = self.day_start
        end = self.end_time
        compose_end_date = datetime(day=day,time=end)
        return compose_end_date

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
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    multi_occurrence_model = models.ForeignKey(MultiOccurrenceModel,on_delete=models.SET_NULL,null=True, blank=True)
    objects = OccurrenceManager()

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
