from django.test import TestCase
from models import Event,RoomCalendarModel,TenantModel,OccurrenceModel
from django.contrib.auth import get_user_model
from django.utils import timezone
import pendulum as p
# Create your tests here.


class EventOccurrenceTest(TestCase):
    # Event creation

    # Occurrences of event creation

    # Occurrences list
    ...


class CalendarOccurrenceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = p.instance(timezone.now())
        cls.user = get_user_model().objects.create(username="Gabriel",email="test@gabriel.cl")
        cls.user_host = get_user_model().objects.create(username="John",email="test@john.cl")
        cls.tenant = TenantModel.objects.create(
                        user=cls.user,
                        name="Testing",
                        description="Testing tenancy",

        )
        cls.room_1 = RoomCalendarModel.objects.create(
                        user=cls.user_host, 
                        name="Blue", 
                        description="Testing Blue Room", 
                        tenants=[cls.tenant,],
        )
        cls.room_2 = RoomCalendarModel.objects.create(
                        user=cls.user_host, 
                        name="Green", 
                        description="Testing Green Room", 
                        tenants=[cls.tenant,],
        )
        cls.event = Event.objects.create(
                        user=cls.user,
                        room_calendar=cls.room_1,
                        client=None, # link to client test? (second level testing)
                        title="Monica",
                        description="Supervision",
                        event_type="sup",
        )
        cls.occurrence_1 = OccurrenceModel.objects.create(
                        duration="fill",
                        end_time="fill",
                        event="fill",
                        objects="fill",
                        calendar="fill",

        )
        cls.occurrence_2 = OccurrenceModel.objects.create(
                        duration="fill",
                        end_time="fill",
                        event="fill",
                        objects="fill",
                        calendar="fill",

        )
                            
    # Week View
    def week_view_display(self):
        ...
    
    def week_view_switch(self):
        ...


    # Day View

    # Month select?


class TenantCalendarTest(TestCase):
    # Calendar create

    # Tenant Create

    # Tenant by calendar
    ...