from datetime import datetime
from dateutil import rrule
from datetime import datetime, date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.validators import int_list_validator

import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from .conf import swingtime_settings
from choices import *

class TenantModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200,blank=True)
    class Meta:
        verbose_name = "tenant"
        verbose_name_plural = "tenants"
        ordering = "name"
    def __str__(self):
        return self.name

class RoomCalendar(models.Model):
    """ a room calendar model that will hold the events """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    name = models.CharField(default="",max_length=20)
    description = models.CharField(default="",max_length=200)
    tenants = models.ManyToManyField(TenantModel,related_query_name="tenants")
    class Meta:
        verbose_name = "room calendar"
        verbose_name_plural = "room calendars"
        ordering = "name"
    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Container model for general metadata and associated ``Occurrence`` entries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_calendar = models.ForeignKey(RoomCalendar,on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=100)
    event_type = models.CharField(choices=EVENT_TYPE, verbose_name="event type")

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = "title"

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
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)
    
    def add_single_occurrence(self,event, start_time, end_time):
        """adds one occurrence of this event"""
        self.occurrence_set.create(start_time=start_time, end_time=end_time)


class MultiOccurrenceModel(models.model):
    """ Model that holds the multiple occurrences setting of an Event """
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    day = models.DateField(default=date.today) # todo add date select widget in forms
    start_time = models.IntegerField(choices=default_timeslot_options)
    end_time = models.IntegerField(choices=default_timeslot_options)
    # recurrence options
    until = models.DateField(required=False, default=date.today)
    frequency = models.IntegerField(default=rrule.WEEKLY,choices=FREQUENCY_CHOICES)
    interval = models.IntegerField(required=False,default=1)
    # weekly options
    week_days_1 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    week_days_2 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    week_days_3 = models.IntegerField(choices=WEEKDAY_SHORT,blank=True)
    # monthly options
    month_option = models.CharField(validators=int_list_validator,choices=ON_EACH,default="each")
    month_ordinal = models.IntegerField(choices=ORDINAL,required=False) # which week of month
    month_ordinal_day = models.IntegerField(choices=WEEKDAY_LONG,required=False) #which day of that week
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
                params["bymonthday"] = data["each_month_day"]

        elif self.frequency != rrule.DAILY:
            raise NotImplementedError(_("Unknown interval rule " + self.frequency))
        return params
    
    def add_occurrences(self):
        """
        adds multiple occurrences of this event
        """
        rrule_params = self._build_rrule_params()
        until = rrule_params.get("until")
        event = time(self.event)
        start_time = time(self.start_time)
        end_time = self.end_time
        if until:
            rrule_params.setdefault("freq", rrule.DAILY)
            event_duration = end_time - start_time
            occurrences = []
            for date_instance in rrule.rrule(dtstart=start_time, **rrule_params):
                occurrences.append(
                    Occurrence(start_time=date_instance, end_time=date_instance + event_duration, event=event)
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

class OccurrenceManager(models.Manager):
    def daily_occurrences(self, dt=None, event=None):
        """
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
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


class Occurrence(models.Model):
    """
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField("start time")
    end_time = models.DateTimeField("end time")
    event = models.ForeignKey(
        Event, verbose_name="event", editable=False, on_delete=models.CASCADE
    )
    multi_occurrence_model = models.ForeignKey(MultiOccurrenceModel,on_delete=models.PROTECT)
    objects = OccurrenceManager()

    class Meta:
        verbose_name ="occurrence"
        verbose_name_plural = _("occurrences")
        ordering = ("start_time", "end_time")
        base_manager_name = "objects"

    def __str__(self):
        return "{}: {}".format(self.title, self.start_time.isoformat())

    def get_absolute_url(self):
        return reverse("swingtime-occurrence", args=[str(self.event.id), str(self.id)])

    def __lt__(self, other):
        return self.start_time < other.start_time

    @property
    def title(self):
        return self.event.title

    @property
    def event_type(self):
        return self.event.event_type


def create_event(
    title,
    event_type,
    description="",
    start_time=None,
    end_time=None,
    note=None,
    **rrule_params
):
    """
    Convenience function to create an ``Event``, optionally create an
    ``EventType``, and associated ``Occurrence``s. ``Occurrence`` creation
    rules match those for ``Event.add_occurrences``.

    Returns the newly created ``Event`` instance.

    Parameters

    ``event_type``
        can be either an ``EventType`` object or 2-tuple of ``(abbreviation,label)``,
        from which an ``EventType`` is either created or retrieved.

    ``start_time``
        will default to the current hour if ``None``

    ``end_time``
        will default to ``start_time`` plus swingtime_settings.DEFAULT_OCCURRENCE_DURATION
        hour if ``None``

    ``freq``, ``count``, ``rrule_params``
        follow the ``dateutils`` API (see http://labix.org/python-dateutil)

    """

    if isinstance(event_type, tuple):
        event_type, created = EventType.objects.get_or_create(
            abbr=event_type[0], label=event_type[1]
        )

    event = Event.objects.create(
        title=title, description=description, event_type=event_type
    )

    start_time = start_time or datetime.now().replace(minute=0, second=0, microsecond=0)

    end_time = end_time or (start_time + swingtime_settings.DEFAULT_OCCURRENCE_DURATION)
    event.add_occurrences(start_time, end_time, **rrule_params)
    return event
