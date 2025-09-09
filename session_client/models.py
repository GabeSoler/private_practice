from pyexpat.errors import messages

from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
from django.urls import reverse

from .choices import ATTENDANCE,CLIENT_TYPE,WEEKDAY_SHORT,duration_times_as_choices,time_slot_options,SERIES_CHOICE
from room_calendar_app.models import RoomCalendarModel
import pendulum as p
from pgvector.django import VectorField

# Create your models here.

class ClientModel(models.Model):
    class SeriesChoices(models.IntegerChoices):
        WEEKLY = 1, "Every week"
        FORTNIGHT = 2, "Every two weeks"

    """a model to organise clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    room_calendar = models.ForeignKey(RoomCalendarModel,on_delete=models.SET_NULL,blank=True,null=True)
    #Client labels
    code = models.CharField(blank=False,max_length=10,help_text="Add an Identifier code") #Create a code instead of name
    nick_name = models.CharField(default="",blank=True,null=True,max_length=20,help_text="Give it a memorable nickname")
    type = models.CharField(default='Pvt', choices=CLIENT_TYPE, max_length=20, help_text="Select a type of client") # add choices like private, service, eap, supervisee
    fee = models.IntegerField(default=50,validators=(MinValueValidator(1),MaxValueValidator(100)),help_text="Whats your agreed fee")
    #client base info(delete after 7 yeas?)(I am thinking to only erase the fields as the admin is yours)
    active = models.BooleanField(default=True,help_text="Change if your client is active or archived")
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


    def deduce_next_datetime(self,after_last=True):
        """deduces the next week's appointment from defaults in ClientModel
        args
            after_last : searches for the last session of this client in the database for reference
            if false, adds for next week
             """
        if after_last:
            last_session = SessionModel.objects.filter(user=self.user,client=self).latest()
            ref_date = last_session.start_datetime or p.now()
            add_weeks = self.series if last_session else 1
            ref_date.add(weeks=add_weeks)
        else:
            ref_date = p.now()
            ref_date.add(weeks=1)
        week_start = ref_date.start_of('week')
        day_of_week:int = self.day
        target_date = week_start.add(days=day_of_week -1)
        return target_date.at(self.time.hour,self.time.minute)



    def add_series(self,amount:int,room_switch=False):
        """ Creates a series of sessions, based on the client defaults
            calculates the last session created first and moves from there
        args:
            amount sets the number of series forwards
        returns:
            Bool,queryset
            True if saved, false if not
            queryset if there is overlap
        """
        next_date = self.deduce_next_datetime()
        interval = p.interval(next_date,next_date.add(weeks=amount-1))
        session_list = []
        step = self.series
        for date in interval.range('weeks',step):
            """ creates a list of sessions to then bulk create"""
            session_instance = SessionModel(
                client=self.client,
                start_datetime=date,
                end_datetime=date+self.duration,
                room=self.room_calendar
            )

            session_list.append(session_instance)
        fortnight = True if self.series == 2 else False
        possible_overlap = self.check_series_overlap(interval.start,interval.end,fortnight=fortnight)
        if possible_overlap:
            """ possible overlap is checking if there are sessions on the expected dates """
            if room_switch:
                saved, overlap = self.add_series(amount)
                if saved:
                    messages.warning("❗️Saved in Base Calendar")
            messages.info("Thera is an overlap")
            return False,possible_overlap
        else:
            SessionModel.objects.bulk_create(session_list)
            messages.info(f"✅ {len(session_list)}Sessions Created")
            return True,None

    def check_series_overlap(self,start_range,end_range,fortnight=False):
        """ checks if there are sessions on the same date range with the same times
        args:
            start range: when to start
            end range: when to end
            fortnight: if skip every other week
        returns:
            query of overlaps
        """
        start = self.time
        end = self.time + self.duration
        if fortnight:
            exclude_int = p.interval(start_range.add(weeks=1),end_range)
            exclude_range = [x for x in exclude_int.range('weeks',2)]
        else:
            exclude_range = None
        possible_overlap = SessionModel.objects.filter(calendar=self.room_calendar,
                                                       start_datetime__gt=start_range,
                                                       start_datetime__week_day=self.day,
                                                       end_datetime__lte=end_range
                                                       ).filter(models.Q(
            start_datetime__time__gte=start,
            start_datetime__time__lte=end)
            |models.Q(
            end_datetime__time__gte=start,
            end_datetime__time__lte=end,
        )|models.Q(
            start_datetime__lt=start, end_datetime__gt=end
        )).exclude(exclude_range)
        return possible_overlap




class SessionManager(models.Manager):
    pass


class SessionModel(models.Model):
    client = models.ForeignKey(ClientModel,null=True,on_delete=models.CASCADE,help_text="Link to a client")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # datetime fields
    start_datetime = models.DateTimeField(null=True,blank=True, editable=True,help_text="Start of session?")
    end_datetime = models.DateTimeField(null=True,blank=True, editable=True,help_text="End of session")
   #Session notes and vector(delete after 7 years?)
    brief = models.CharField(default='',blank=True,max_length=250,help_text="250 characters note") #short description
    brief_vector = VectorField(dimensions=3,null=True) #for vector search
    #admin info
    paid = models.BooleanField(default=False,blank=True) #check payment
    attended = models.CharField(default='',blank=True,max_length=20,choices=(ATTENDANCE)) #record attendance
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
        ordering = ("start_datetime",)
        base_manager_name = "objects"
        get_latest_by = "start_datetime"


    def __str__(self):  # noqa: F811
        ref_date = self.start_datetime or ""
        return f"{self.brief[:8]}:{ref_date}"


    def __lt__(self, other):
        return self.start_datetime < other.start_datetime

    def overlap_set(self):
        """
        Returns a queryset of for instances that have any overlap with a
        particular room and time frame.
        """
        start = self.start_datetime
        end = self.end_datetime
        calendar = self.calendar
        qs = SessionModel.objects.filter(calendar=calendar).filter(
            models.Q(
                start_datetime__gte=start,
                start_datetime__lte=end,
            )
            | models.Q(
                end_datetime__gte=start,
                end_datetime__lte=end,
            )
            | models.Q(start_datetime__lt=start, end_datetime__gt=end)
        ).exclude(pk=self.pk)
        return qs

    def is_unique(self):
        """ takes a Session and checks if overlaps with others.
            Returns (True, None) if it does not overlap, and (False,Queryset) if it does  """

        overlaps = self.overlap_set()
        if overlaps:
            __bool__ = False
            return False, overlaps
        else:
            __bool__ = True  # noqa: F841
            return True, None

    def deduce_from_client(self,start_datetime=None,room=None):
        """ takes a Session with a client, and deduces from it its room, and extra information about when it happens
        args:
            start_datetime: if you want to set a with clear datetime object. If present it blocks next args.
            room : to override the room of the client
            add_weeks : to deduce nex week or more weeks ahead when it should be a session
            ref date: allows to set session from a reference date. If added week, it will use the date and add to it.
        returns: empty

        """
        assert self.client is not None
        client = self.client
        if room:
            """ deducing the appropriate room"""
            self.calendar = room
        else:
            if client.room_calendar:
                self.calendar = client.room_calendar
            else:
                base_cal,_ = RoomCalendarModel.objects.get_or_create(user=self.client.user,name="Base Room")
                self.calendar = base_cal
        if start_datetime:
            self.start_datetime = start_datetime
            self.end_datetime = start_datetime + client.duration
            return
        start = client.deduce_next_datetime()
        self.start_datetime = start
        self.end_datetime = start + client.duration
        return


    @property
    def week_day(self):
        return self.start_datetime.day