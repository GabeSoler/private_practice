
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
import uuid

from django.urls import reverse

from .choices import ATTENDANCE,CLIENT_TYPE,WEEKDAY_SHORT,duration_times_as_choices,time_slot_options,SERIES_CHOICE
from room_calendar_app.models import RoomCalendarModel
import pendulum as p
from pgvector.django import VectorField

from .utils import time_plus_duration,date_plus_time,range_from_date


# Create your models here.

class ClientModel(models.Model):
    """a model to organise clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    calendar = models.ForeignKey(RoomCalendarModel, on_delete=models.SET_NULL, blank=True, null=True)
    #Client labels
    code = models.CharField(blank=False,max_length=10,help_text="Add an Identifier code") #Create a code instead of a name
    nick_name = models.CharField(default="",blank=True,null=True,max_length=20,help_text="Give it a memorable nickname")
    type = models.CharField(default='Pvt', choices=CLIENT_TYPE, max_length=20, help_text="Select a type of client") # add choices like private, service, eap, supervisee
    fee = models.IntegerField(default=50,validators=(MinValueValidator(1),MaxValueValidator(100)),help_text="Whats your agreed fee")
    #client base info (delete after 7 yeas?)(I am thinking to only erase the fields as the admin is yours)
    active = models.BooleanField(default=True,help_text="Move from archive to active or viceversa")
    archived_at = models.DateTimeField(blank=True,null=True)
    day = models.IntegerField(choices=WEEKDAY_SHORT,default=1,help_text="Default day of week")
    time = models.TimeField(choices=time_slot_options(),help_text='default time')
    duration = models.DurationField(default='60 minutes',choices=duration_times_as_choices(),help_text='default duration')
    series = models.IntegerField(default=1,choices=SERIES_CHOICE)

    class Meta:
        verbose_name ="Client"
        verbose_name_plural = "Clients"
        ordering = ("code", "created_at")


    @property
    def color_class(self):
        """ Property to add a colour class when listing clients """
        match self.type:
            case 'Pvt':
                return 'primary'
            case 'Srv':
                return 'secondary'
            case 'EAP':
                return 'danger'
            case 'Sp':
                return 'warning'
            case 'CPD':
                return 'info'
        return None

    def __str__(self):
        return f"{self.code}"
    
    def get_absolute_url(self):
        return reverse("session_client:client", kwargs={"client_pk":self.pk})


    def deduce_next_datetime(self):
        """deduces the next week's appointment from defaults in ClientModel
        if the session is later than tomorrow, use it as reference, else use today
        this is to avoid creating sessions in the past.
             """
        last_session = SessionModel.objects.filter(client=self).latest() or None
        last_date = p.date(last_session.date.year, last_session.date.month, last_session.date.day)
        if last_date >= p.now().add(days=1).date():
            # if it is more than now, use it as a reference date
            ref_date = p.now().on(last_date.year, last_date.month, last_date.day).start_of('day')
        else:
            ref_date = p.now()
        add_weeks = self.series if last_session else 1
        ref_date.add(weeks=add_weeks)
        week_start = ref_date.start_of('week')
        day_of_week:int = self.day
        target_date = week_start.add(days=day_of_week)
        assert target_date.day_of_week == self.day, f"{target_date.day_of_week} != {self.day}::Day of week does not match"
        return target_date.at(self.time.hour,self.time.minute)



    def add_series(self,amount:int,from_date=None, room_switch=False):
        """ Creates a series of sessions, based on the client defaults
            calculate the last session created first and move from there
        args:
            amount sets the number of series forwards
            from_date: if you want to start from a specific date
            room switch tries with the base room. Handle from view to communicate with user messages
        returns:
            Bool,queryset
            True if saved, false if not
            queryset, overlap or saved sessions
        """
        ref_date = from_date or self.deduce_next_datetime()
        next_date = ref_date.at(self.time.hour,self.time.minute)
        interval = p.interval(next_date,next_date.add(weeks=amount-1))
        session_list = []
        step = self.series or 1
        if room_switch:
            room_cal = RoomCalendarModel.objects.get(user=self.user,name="Base Room")
        else:
            room_cal = self.calendar
        for date in interval.range('weeks',step):
            """ creates a list of sessions to then bulk create"""
            session_instance = SessionModel(
                client=self,
                date=date.date(),
                start_time=self.time,
                end_time=time_plus_duration(self.time, self.duration),
                calendar=room_cal,
                brief="Series"
            )

            session_list.append(session_instance)
        fortnight = True if self.series == 2 else False
        possible_overlap = self.check_series_overlap(interval.start,interval.end,fortnight=fortnight)
        if possible_overlap:
            return False,possible_overlap
        else:
            sessions = SessionModel.objects.bulk_create(session_list)
            return True,sessions

    def check_series_overlap(self, start_range:p.Date, end_range:p.Date,
                             fortnight=False,
                             calendar=None,
                             range_filter=True,
                             calendar_filter=True,
                             iso_day_filter=True,
                             time_filter=True,):
        """ checks if there are sessions on the same date range with the same times
        args:
            start range: when to start
            end range: when to end
            fortnight: if skip every other week
        returns:
            query of overlaps
        """
        fortnight = fortnight
        calendar_ref = calendar or self.calendar
        assert calendar_ref is not None, "calendar field is necessary"
        start_time = self.time
        end_time = time_plus_duration(self.time, self.duration)
        start_range_p = start_range
        end_range_p = end_range
        assert isinstance(start_time, p.Time), "start time should be a datetime.time object"
        assert isinstance(end_time, p.Time), "end time should be a datetime.time object"
        # base query sets the calendar, start and end of range, and day of week.

        filters = Q()
        if range_filter:
            filters &=  Q(date__range=(start_range_p,end_range_p))
        if calendar_filter:
            filters &= Q(calendar=calendar_ref)
        if iso_day_filter:
            filters &= Q(date__iso_week_day=self.day)
        if time_filter:
            filters &= Q(
            Q(start_time__gt=start_time,
                     start_time__lt=end_time)| # start between start and end
            Q(end_time__gt=start_time,
                     end_time__lt=end_time)| # ends between start and end
            Q(start_time__lt=start_time,
                     end_time__gt=end_time)) # starts before and finishes after
        possible_overlap = SessionModel.objects.filter(filters)
        if fortnight:
            interval_exclude = range_from_date(start_range_p, end_range_p, fortnight, add_week=True)
            exclude_range = [x.date() for x in interval_exclude.range('weeks',2)]
            possible_overlap = possible_overlap.exclude(start_date__in=exclude_range)
        return possible_overlap




class SessionManager(models.Manager):
    pass


class SessionModel(models.Model):
    client = models.ForeignKey(ClientModel,null=True,on_delete=models.CASCADE,help_text="Link to a client")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # datetime fields
    date = models.DateField(blank=True,default="2025-10-3",help_text="Date of session")
    start_time = models.TimeField(editable=True, default="09:00:00", help_text="Start of session?")
    end_time = models.TimeField(default="10:00:00",blank=True,editable=True, help_text="End of session")
   #Session notes and vector (delete after 7 years?)
    brief = models.CharField(default='',blank=True,max_length=250,help_text="250 characters note") #short description
    brief_vector = VectorField(dimensions=3,null=True) #for vector search
    #admin info
    paid = models.BooleanField(default=False,blank=True) #check payment
    attended = models.CharField(default='', blank=True, max_length=20, choices=ATTENDANCE) #record attendance
    amount_paid = models.IntegerField(default=0,blank=True) #record attendance
    open = models.BooleanField(default=True,blank=True)
    #manager
    objects = SessionManager()
    # Calendar connection
    calendar = models.ForeignKey(RoomCalendarModel,null=True,blank=True,on_delete=models.SET_NULL)

    def __str__(self):
        brief = self.brief
        return f"Session-{brief[:10]}"
    
    def get_absolute_url(self):
        return reverse("session_client:session", kwargs={"session_pk":self.id})
  


    class Meta:
        verbose_name ="session"
        verbose_name_plural = "sessions"
        ordering = ("date","start_time")
        base_manager_name = "objects"
        get_latest_by = "date"


    def __str__(self):  # noqa: F811
        ref_date = self.start_time or ""
        return f"{self.brief[:8]}:{ref_date}"


    def __lt__(self, other):
        return self.start_time < other.start_time

    def overlap_set(self):
        """
        Returns a queryset of for instances that have any overlap with a
        particular room and time frame.
        """
        start = self.start_time
        end = self.end_time
        calendar = self.calendar
        qs = SessionModel.objects.filter(calendar=calendar).filter(
            models.Q(
                start_time__gt=start,
                start_time__lt=end,
            )
            | models.Q(
                end_time__gt=start,
                end_time__lt=end,
            )
            | models.Q(start_time__lt=start,
                       end_time__gt=end)
        ).exclude(pk=self.pk)
        return qs

    def is_unique(self):
        """ takes a Session and checks if overlaps with others.
            Returns (True, None) if it does not overlap, and (False, Queryset) if it does  """

        overlaps = self.overlap_set()
        if overlaps:
            __bool__ = False
            return False, overlaps
        else:
            __bool__ = True  # noqa: F841
            return True, None

    def deduce_from_client(self,start_time=None,date=None,room=None):
        """ takes a Session with a client, and deduces from it its room, and extra information about when it happens
        args:
            start_time: if you want to set a with clear datetime object. If present, it blocks the next args.
            room : to override the room of the client
            add_weeks : to deduce nex week or more weeks ahead when it should be a session
            ref date: allows setting session from a reference date. If added week, it will use the date and add to it.
        returns: empty

        """
        assert self.client is not None
        client = self.client
        if room:
            """ deducing the appropriate room"""
            self.calendar = room
        else:
            if client.calendar:
                self.calendar = client.calendar
            else:
                base_cal,_ = RoomCalendarModel.objects.get_or_create(user=self.client.user,name="Base Room")
                self.calendar = base_cal
        if start_time:
            self.start_time = start_time
        else:
            start = client.deduce_next_datetime()
        self.start_time = start
        self.end_time = time_plus_duration(start, client.duration)
        return


    @property
    def week_day(self):
        return self.start_time.day