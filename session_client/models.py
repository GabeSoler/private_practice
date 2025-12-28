
from django.db import models
from django.db.models import Q
from ppm_app.settings.base import AUTH_USER_MODEL
import uuid
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from base.choices import ATTENDANCE,CLIENT_TYPE,WEEKDAY_SHORT,duration_times_as_choices,time_slot_options,SERIES_CHOICE
from room_calendar_app.models import RoomCalendarModel, TenantModel
import pendulum as p

from .utils import time_plus_duration,range_from_date
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class ClientModel(models.Model):
    """a model to organise clients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    tenant = models.ForeignKey(TenantModel, on_delete=models.SET_NULL, blank=True, null=True)
    #Client labels
    code = models.CharField(blank=False,max_length=15,help_text=_("Add an Identifier code")) #Create a code instead of a nam)e
    # nick_name = models.CharField(default="",blank=True,null=True,max_length=20,help_text=_("Give it a memorable nickname")
    type = models.CharField(default='Pvt', choices=CLIENT_TYPE, max_length=20, help_text=_("Select a type of client")) # add choices like private, service, eap, supervise)e
    fee = models.DecimalField(blank=True,decimal_places=2,max_digits=10,null=True,default=60,help_text=_("Whats your agreed fee"))
    #client base info (delete after 7 years?) (I am thinking to only erase the fields as the admin is yours)
    active = models.BooleanField(default=True,help_text=_("Move from archive to active or vice versa"))
    archived_at = models.DateTimeField(blank=True,null=True)
    day = models.IntegerField(choices=WEEKDAY_SHORT,default=1,help_text=_("Default day of week"))
    time = models.TimeField(choices=time_slot_options(),help_text=_('default time'))
    duration = models.DurationField(default='60 minutes',choices=duration_times_as_choices(),help_text=_('default duration'))
    series = models.IntegerField(default=1,choices=SERIES_CHOICE)
    link = models.URLField(blank=True,null=True,help_text=_("External link"))

    class Meta:
        app_label = 'session_client'
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

    def get_last_date_or_now(self,get_session=False):
        try:
            last_session = self.sessionmodel_set.filter(date__gte=p.now()).latest('date','start_time')
            last_date = last_session.date
            ref_date = p.now().on(last_date.year,last_date.month,last_date.day)
        except SessionModel.DoesNotExist:
            ref_date = p.now()
        if get_session:
            return ref_date,last_session
        return ref_date

    def deduce_next_datetime(self,add_weeks=None):
        """deduces the next week's appointment from defaults in ClientModel
        if the session is later than tomorrow, use it as reference, else use today
        this is to avoid creating sessions in the past.
        args:
            get_session returns two arguments, the date and the session used to calculate it
             """
        ref_date = self.get_last_date_or_now()
        target_date = ref_date.next(self.day)
        if self.series == 2:
            target_date = target_date.add(weeks=1)
        if add_weeks:
            target_date = target_date.add(weeks=add_weeks)
        return target_date



    def add_series(self,amount:int,add_weeks=None,overlap_check=True):
        """ Creates a series of sessions, based on the client defaults,
            calculate the last session created first and move from there
        args:
            amount sets the number of series forwards
            from_date: if you want to start from a specific date,
            room switch tries with the base room. Handle from view to communicate with user messages
        returns:
            Bool,queryset
            True if saved, false if not
            queryset, overlap or saved sessions
        """
        ref_date = self.deduce_next_datetime(add_weeks=add_weeks)
        ref_date = ref_date
        fortnight = True if self.series == 2 else False
        range_weeks = amount * 2 if fortnight else amount -1 # double of weeks if a fortnight,take one week as starts on day
        interval = p.interval(ref_date,ref_date.add(weeks=range_weeks))
        assert isinstance(ref_date,p.DateTime)
        assert ref_date.day_of_week == self.day,f"The ref_date should be on the client.day, {ref_date.day_of_week} != {self.day}"
        session_list = []
        step = self.series or 1
        if self.tenant:
            tenant = self.tenant
        else:
            logger.debug("Using base tenant to set a series")
            tenant,_ = TenantModel.objects.get_or_create(user=self.user,
                                                         name=self.user.username,
                                                         display_name=self.user.username)
        if overlap_check:
            """ stops the process to check for overlaps and returns overlaps"""
            possible_overlap = self.check_series_overlap(interval.start,interval.end,fortnight=fortnight)
            if possible_overlap:
                logger.warning(f"Overlap on series attempt, length: {len(possible_overlap)}")
                __bool__=False
                return False,possible_overlap

        for date in interval.range('weeks',step):
            """ creates a list of sessions to then bulk create"""
            session_instance = SessionModel(
                client=self,
                date=date.date(),
                start_time=self.time,
                end_time=time_plus_duration(self.time, self.duration),
                calendar=tenant.calendar,
                amount_paid=self.fee
            )

            session_list.append(session_instance)
        sessions = SessionModel.objects.bulk_create(session_list)
        sessions_len = len(sessions)
        logger.debug("Sessions created, length: {}",sessions_len)
        assert sessions_len == amount,f"sessions created must match amount, {sessions_len} != {amount}"
        __bool__= True
        return True,sessions

    def check_series_overlap(self, start_range:p.DateTime,
                             end_range:p.DateTime,
                             fortnight=False,
                             calendar=None,
                             range_filter=True,
                             calendar_filter=True,
                             week_day_filter=True,
                             time_filter=True,
                             cancel_filter=True):
        """ checks if there are sessions on the same day/times in the range set
        args:
            start range: when to start
            end range: when to end
            fortnight: if skip every other week

                        The filters are mostly for debugging

            range_filter: if consider the range default True
            calendar_filter: if consider the calendar default True
            iso_day_filter: if consider the iso day default True
            time_filter: if consider the time default True
        returns:
            query of overlaps, empty if none
        """
        if calendar:
            calendar_ref = calendar
        elif self.tenant:
            calendar_ref = self.tenant.calendar
        else:
            calendar_ref = RoomCalendarModel.objects.get(user=self.user,name="Base Room")
        assert isinstance(calendar_ref,RoomCalendarModel),"calendar must be a RoomCalendarModel object"
        start_time = self.time
        end_time = time_plus_duration(self.time, self.duration)
        start_range_p = start_range
        end_range_p = end_range
        assert isinstance(start_range_p, p.DateTime), "start_range should be a datetime object"
        assert isinstance(end_range_p, p.DateTime), "end_range should be a datetime object"
        # base query sets the calendar, start and end of range, and day of a week.

        filters = Q()
        if cancel_filter:
            filters &= ~Q(attendance="Cancel")
        if range_filter:
            filters &= Q(date__range=(start_range_p.date(),end_range_p.date()))
        if calendar_filter:
            filters &= Q(calendar=calendar_ref)
        if week_day_filter:
            day_week = self.day + 1 # to convert from a pendulum days system to iso
            filters &= Q(date__iso_week_day=day_week)
        if time_filter:
            filters &= Q(
            Q(start_time__gte=start_time,
                     start_time__lt=end_time)| # starts on the same start (or more) inside the range
            Q(end_time__gt=start_time,
                     end_time__lte=end_time)| # ends between start and end
            Q(start_time__lt=start_time,
                     end_time__gt=end_time)) # starts before and finishes after the range
        possible_overlap = SessionModel.objects.filter(filters)
        if fortnight:
            interval_exclude = range_from_date(start_range_p, end_range_p, step=2, add_weeks=1)
            exclude_range = [x.date() for x in interval_exclude.range('weeks',2)]
            possible_overlap = possible_overlap.exclude(date__in=exclude_range)
        if possible_overlap:
            logger.debug("possible overlap function found overlap")
        return possible_overlap




class SessionManager(models.Manager):
    pass



class SessionModel(models.Model):
    client = models.ForeignKey(ClientModel,null=True,on_delete=models.CASCADE,help_text=_("Link to a client"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # datetime fields
    date = models.DateField(blank=True,default="2025-10-3",help_text=_("Date of session"))
    start_time = models.TimeField(editable=True, default="09:00:00", help_text=_("Start of session?"))
    end_time = models.TimeField(default="10:00:00",blank=True,editable=True, help_text=_("End of session"))
   #Session notes and vector (delete after 7 years?)
    # brief = EncryptedCharField(default='',null=True,blank=True,max_length=250,help_text=_("250 characters note") #short descriptio)n
    keywords = models.CharField(blank=True,max_length=25,help_text=_("words for search"))
    #admin info
    paid = models.BooleanField(default=False,blank=True) #check payment
    attendance = models.CharField(default='', blank=True, max_length=20, choices=ATTENDANCE) #record attendance
    fee = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True,default=60.00)
    open = models.BooleanField(default=True,blank=True)
    #manager
    objects = SessionManager()
    # Calendar connection
    calendar = models.ForeignKey(RoomCalendarModel,null=True,blank=True,on_delete=models.SET_NULL)


    def get_absolute_url(self):
        return reverse("session_client:session", kwargs={"session_pk":self.id})
  


    class Meta:
        app_label = 'session_client'
        verbose_name ="session"
        verbose_name_plural = "sessions"
        ordering = ("date","start_time")
        base_manager_name = "objects"
        get_latest_by = "date"


    def __str__(self):  # noqa: F811
        ref_date = self.start_time or ""
        return f"{self.client}::{self.date},{ref_date}"


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
        qs = SessionModel.objects.filter(calendar=calendar,date=self.date).filter(
            models.Q(
                start_time__gte=start,
                start_time__lt=end,
            )
            | models.Q(
                end_time__gt=start,
                end_time__lte=end,
            )
            | models.Q(start_time__lt=start,
                       end_time__gt=end)
        ).exclude(pk=self.pk).select_related("client","client__tenant")
        return qs

    def is_unique(self):
        """ checks individual session overlap.
            Returns (True, None) if it does not overlap, and (False, Queryset) if it does  """

        overlaps = self.overlap_set()
        if overlaps:
            __bool__ = False
            return False, overlaps
        else:
            __bool__ = True
            return True, None

    def save_with_checks(self):
        unique,overlaps = self.is_unique()
        if unique:
            self.save()
            return True, overlaps
        else:
            return False, overlaps



    def deduce_from_client(self,
                           date=True,
                           start_time=True,
                           end_time=True,
                           calendar=True):
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
        if calendar:
            if client.tenant:
                self.calendar = client.tenant.calendar
            else:
                base_cal,_ = RoomCalendarModel.objects.get_or_create(user=self.client.user,name="Base Room")
                self.calendar = base_cal
        if date:
            self.date = client.deduce_next_datetime().date()
        if start_time:
            self.start_time = client.time
        if end_time:
            self.end_time = time_plus_duration(self.start_time, client.duration)
        return self
