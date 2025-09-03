from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
from django.urls import reverse

from .choices import ATTENDANCE,CLIENT_TYPE,WEEKDAY_SHORT,duration_times_as_choices,time_slot_options
from room_calendar_app.models import RoomCalendarModel
import pendulum as p
from pgvector.django import VectorField

# Create your models here.

class ClientModel(models.Model):
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

    class Meta:
        ordering = ("updated_at", "code")
        verbose_name ="Client"
        verbose_name_plural = "Clients"
        # noinspection PyRedeclaration
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


    def deduce_next_datetime(self,add_weeks=1,ref_date=p.now(),set_time=None):
        """deduces the next week's appointment from defaults in ClientModel"""
        if add_weeks:
            ref_date = ref_date.add(weeks=add_weeks)
        week_start = ref_date.start_of('week')
        day_of_week:int = self.day
        target_date = week_start.add(days=day_of_week - 1)
        time = set_time or self.time
        return target_date.at(time.hour,time.minute)





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
        qs = SessionModel.objects.filter(room_calendar=calendar).filter(
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

    def deduce_from_client(self,start_datetime=None,room=None,add_weeks:int=None,ref_date=None):
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
        self.room_calendar = room or client.room_calendar
        if start_datetime:
            self.start_datetime = start_datetime
            self.end_datetime = start_datetime + client.duration
            return
        start = client.deduce_next_datetime(add_weeks=add_weeks,ref_date=ref_date)
        self.start_datetime = start
        self.end_datetime = start + client.duration
        return


    @property
    def week_day(self):
        return self.start_datetime.day