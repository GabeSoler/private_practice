from django.test import TestCase
from .models import Event,RoomCalendarModel,TenantModel,OccurrenceModel
from .forms import WeekCalendarForm
from django.contrib.auth import get_user_model
from django.utils import timezone
import pendulum as p
from datetime import timedelta
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
        cls.user.save()
        cls.user_host = get_user_model().objects.create(username="John",email="test@john.cl")
        cls.user_host.save()
        cls.tenant = TenantModel(
                        user=cls.user,
                        name="Testing",
                        description="Testing tenancy")
        cls.tenant.save()
        cls.room_1 = RoomCalendarModel(
                        user=cls.user_host, 
                        name="Blue", 
                        description="Testing Blue Room", 
        )
        cls.room_1.tenants.add(cls.tenant)
        cls.room_1.save()
        cls.room_2 = RoomCalendarModel(
                        user=cls.user_host, 
                        name="Green", 
                        description="Testing Green Room", 
        )
        cls.room_2.tenants.add(cls.tenant)
        cls.room_2.save()

        cls.event = Event.objects.create(
                        user=cls.user,
                        room_calendar=cls.room_1,
                        client=None, # link to client test? (second level testing)
                        title="Monica",
                        description="Supervision",
                        event_type="sup",
        ).save()
        cls.occurrence_1 = OccurrenceModel.objects.create(
                        duration=timedelta(minutes=90),
                        start_time=cls.now.at(8), 
                        end_time=cls.now.at(9,30),
                        event=cls.event,
                        calendar=cls.room_1,
        )
        cls.occurrence_1.save()
        cls.occurrence_2 = OccurrenceModel.objects.create(
                        duration=timedelta(minutes=60),
                        start_time=cls.now.add(weeks=1), 
                        end_time=cls.now.add(weeks=1,hours=1),
                        event=cls.event,
                        calendar=cls.room_2,

        )
        cls.occurrence_2.save()
        cls.calendar_data = {
                'calendar':cls.room_1,
                'date':cls.now.add(weeks=1).date(),
        }
        cls.calendar_data_2 ={
                'calendar':"",
                'date':"12/03/25",
        }
    

    def test_form_week_view(self):
        self.client.force_login(self.user)
        form_invalid = WeekCalendarForm(data={"calendar": "Computer", "data": 400.1234})
        self.assertFalse(form_invalid.is_valid())
        form_valid = WeekCalendarForm(data=self.calendar_data)
        form_valid.is_valid()
        form_valid_2 = WeekCalendarForm(data=self.calendar_data_2)
        form_valid_2.is_valid()
        print(form_valid.errors.as_data())
        self.assertTrue(form_valid.is_valid())
        self.assertTrue(form_valid_2.is_valid()) #testing form with two types of data
        
    def test_week_view__today_render(self):
        self.client.force_login(self.user)
        start_time = p.instance(self.occurrence_1.start_time)
        end_time = p.instance(self.occurrence_1.end_time)
        response = self.client.get('/calendar/week-view/')
        self.assertContains(response,f"{self.now.format("DD-MM-YY")}")
        self.assertContains(response,f"{self.user.username}- {start_time.format("HH:mm")}- {end_time.format("HH:mm")}")
        response = self.client.post('calendar/week-view/',self.calendar_data, follow=True)
        self.assertEqual(response.status_code,200)

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