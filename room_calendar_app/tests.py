from pprint import pprint

from django.test import TestCase
from .models import RoomCalendarModel,TenantModel
from .forms import WeekCalendarForm
from django.contrib.auth import get_user_model
from django.utils import timezone
import pendulum as p
from datetime import timedelta
from .calendar_utils import CalendarRender
from session_client.models import ClientModel,SessionModel
# Create your tests here.




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

        # Create a client (equivalent to event)
        cls.client = ClientModel.objects.create(
            user=cls.user,  # assuming you have cls.user defined
            code="Test123",
            time=p.now().at(8, 0).time(),
            duration=timedelta(hours=1),
        )
        cls.client.save()

        # Create sessions (equivalent to occurrences)
        cls.session_1 = SessionModel.objects.create(
            client=cls.client,
            start_datetime=cls.now.at(8, 0),  # 8:00
            end_datetime=cls.now.at(9, 30),  # 9:30
            calendar=cls.room_1,  # assuming you have cls.room_1 defined
            title="Test Session 1"
        )

        cls.session_1.save()
        cls.session_2 = SessionModel.objects.create(
            client=cls.client,
            start_datetime=cls.now.add(weeks=1).at(8, 0, 0),  # Next week same time
            end_datetime=cls.now.add(weeks=1, hours=1).at(9, 30, 0),  # Next week +1 hour
            calendar=cls.room_2,  # assuming you have cls.room_2 defined
            title="Test Session 2"
        )
        cls.session_2.save()

        cls.calendar_data = {
                'calendar':cls.room_1,
                'date_reference':cls.now.add(weeks=1).date(),
        }
        cls.calendar_data_2 ={
                'calendar':"",
                'date_reference':"12/03/25",
        }
    

    def test_form_week_view(self):
        self.client.force_login(self.user)
        form_invalid = WeekCalendarForm(data={"calendar": "Computer", "data": 400.1234})
        self.assertFalse(form_invalid.is_valid())
        form_valid = WeekCalendarForm(data=self.calendar_data)
        self.assertTrue(form_valid.is_valid())
        form_valid_2 = WeekCalendarForm(data=self.calendar_data_2)
        self.assertTrue(form_valid_2.is_valid())
        form_valid_2.is_valid()
        print(form_valid.errors.as_data())
        self.assertTrue(form_valid_2.is_valid()) #testing form with two types of data
        
    def test_week_view_today_render(self):
        self.client.force_login(self.user)
        start_time = self.session_1.start_datetime
        end_time = self.session_1.end_datetime
        response = self.client.get('/calendar/week-view/')
        expected_string = f"{self.user.username}- {start_time.format('HH:mm')}- {end_time.format('HH:mm')}"
        self.assertContains(response,expected_string)
        response = self.client.post('calendar/week-view/',self.calendar_data, follow=True)
        self.assertEqual(response.status_code,200)

    def test_week_dict_utils(self):
        sessions = SessionModel.objects.all()
        calendar_render = CalendarRender(sessions,self.now)
        session = sessions[1]
        start_time = session.start_datetime.time()
        week_day = session.start_datetime.isoweekday()
        self.assertEqual(calendar_render.week_dict[start_time][week_day],session)



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


