from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model
import uuid
from django.urls import reverse
from .choices import ATTENDANCE,CLIENT_TYPE,WEEKDAY_SHORT,duration_times_as_choices,time_slot_options
from room_calendar_app.models import RoomCalendarModel
import pendulum as p
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
    def color_class(self): #to add a colour class or other relative to event type
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



class SessionManager(models.Manager):
    def create_unique(self,client,date=None,time=None,duration=None,room=None):
        """ creates an Session and checks if overlaps with others. 
            Returns (True, None) if it does not overlap, and (False,Queryset) if it does  """
        if date is None:
            # deducing next's weeks appointment from defaults in ClientModel
            now = p.now()
            week_day:int = client.day
            now_day_week = now.isoweekday()
            if now_day_week < week_day:
                diff = week_day - now_day_week
                date = now.add(weeks=1,days=diff)
            else:
                diff = now_day_week - week_day
                date = now.add(weeks=1).subtract(days=diff)
        start_time = date + time
        end_time = start_time + duration
        calendar = room if room else client.room_calendar
        new_occ = self.create(
            start_time=start_time,
            end_time=end_time,
            client=client,
            calendar=calendar,
        )
        overlaps = new_occ.overlap_set()
        if overlaps:
            __bool__ = False
            return overlaps
        else:
            __bool__ = True  # noqa: F841
            return None



class SessionModel(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    client = models.ForeignKey(ClientModel,on_delete=models.CASCADE,help_text="Link to a client")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    start_datetime = models.DateTimeField(null=True,blank=True, editable=True,help_text="Start of session?")
    end_datetime = models.DateTimeField(null=True,blank=True, editable=True,help_text="End of session")
   #Session labels(delete after 7 years?)
    title = models.CharField(default='',blank=True,max_length=200,help_text="Give the session a title") #short description
    notes = models.TextField(default='',blank=True,help_text="Longer note of Session") #longer description
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
        title = self.title
        return f"Session-{title[:10]}"
    
    def get_absolute_url(self):
        return reverse("session_client:session", kwargs={"session_pk":self.id})
  


    class Meta:
        verbose_name ="session"
        verbose_name_plural = "sessions"
        ordering = ("start_datetime",)
        base_manager_name = "objects"

    def __str__(self):  # noqa: F811
        ref_date = self.start_datetime or ""
        return f"{self.title}: {ref_date}"

    def get_absolute_url(self):  # noqa: F811
        return reverse("session_client:edit_session", args=[str(self.id)])

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

    @property
    def week_day(self):
        return self.start_datetime.day