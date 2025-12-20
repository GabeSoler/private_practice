from django.test import TestCase
from django.urls import reverse

from .models import RoomCalendarModel, TenantModel
from .forms import WeekCalendarForm
from django.contrib.auth import get_user_model
import pendulum as p
from datetime import timedelta
from .calendar_utils import CalendarRender
from session_client.models import ClientModel, SessionModel


# Create your tests here.


class MetaTestSetupMixin:
    """ **Sets up the whole ecosystem of models to be able to test**
    It allows testing the integration of sessions, clients, tenant and calendars
    self.user : a test user
    self.user_host a second user
    self.tenant a tenant account for user
    self.room1 A room from user_host with user as tenant
    self.room_default a default room for user
    self.client_instance, a client for user
    self.session_1 today 8 am to 8.30
    self.session_2 next week 8-9 am
    self.calendar_data for testing calendar form
    self.htmx headers : to send data as htmx
    self.session_list a list of sessions created for tomorrow
    """

    @classmethod
    def setUpTestData(cls):
        cls.now = p.now("UTC")
        cls.user = get_user_model().objects.create(username="Gabriel", email="test@gabriel.cl")
        cls.user.save()
        cls.user_host = get_user_model().objects.create(username="John", email="test@john.cl")
        cls.user_host.save()
        cls.room_1 = RoomCalendarModel(
            user=cls.user_host,
            name="Blue",
            description="Testing Blue Room",
        )
        cls.room_1.save()
        cls.room_2 = RoomCalendarModel(
            user=cls.user_host,
            name="Green",
            description="Testing Green Room",
        )
        cls.room_2.save()
        cls.room_default = RoomCalendarModel.objects.create(user=cls.user, name="Base Room",
                                                            description="base room user",
                                                            )
        cls.tenant = TenantModel(
            user=cls.user,
            name="Testing",
            display_name="test",
            description="Testing tenancy",
            calendar=cls.room_1)
        cls.tenant.save()

        cls.tenant_host = TenantModel(
            user=cls.user_host,
            name="T-Host",
            display_name="test",
            description="Testing tenancy",
            calendar=cls.room_2)
        cls.tenant_host.save()

        cls.tenant_default,_ = TenantModel.objects.get_or_create(user=cls.user,
                                                     name="Default")


        # Create a client (equivalent to event)
        cls.client_instance = ClientModel.objects.create(
            user=cls.user,
            code="Test123",
            time=p.now().at(8, 0).time(),
            day=p.MONDAY,
            duration=p.duration(hours=1),
            tenant=cls.tenant,
            fee=60,
        )
        cls.client_instance.save()

        # Create sessions (equivalent to occurrences)
        cls.session_1 = SessionModel.objects.create(
            client=cls.client_instance,
            date=p.now().date(),
            start_time=p.time(8, 0),  # 8:00
            end_time=p.time(9, 30),  # 9:30
            calendar=cls.room_1,  # assuming you have cls.room_1 defined
            brief="Session1",
            fee=60,
            paid=True,
            attendance="Attended",

        )
        cls.session_1.save()

        cls.session_2 = SessionModel.objects.create(
            client=cls.client_instance,
            date=p.now().add(weeks=1).date(),
            start_time=p.time(8, 00, 00),  # Next week the same time
            end_time=p.time(9, 30),
            calendar=cls.room_2,
            brief="Session2",
            fee=60,
            paid=False,
            attendance="Attended",

        )
        cls.session_2.save()

        cls.session_overlap_1 = SessionModel.objects.create(
            client=cls.client_instance,
            date=p.now().subtract(weeks=1).date(),
            start_time=p.time(8, 00, 00),  # Next week the same time
            end_time=p.time(9, 30),
            calendar=cls.room_1,
            brief="Overlap1",
            fee=60,
            paid=False,
            attendance="Attended",

        )
        cls.session_overlap_1.save()

        cls.session_overlap_2 = SessionModel.objects.create(
            client=cls.client_instance,
            date=p.now().subtract(weeks=1).date(),
            start_time=p.time(9, 00, 00),  # Next week the same time
            end_time=p.time(10, 30),
            calendar=cls.room_1,
            brief="Overlap2",
            fee=60,
            paid=False,
            attendance="Attended",

        )
        cls.session_overlap_2.save()

        cls.calendar_data = {
            'calendar': cls.room_1,
            'date_reference': cls.now.date(),
        }
        cls.calendar_data_2 = {
            'calendar': "",
            'date_reference': cls.now.add(weeks=1).date(),
        }

        cls.htmx_headers = {
            "HX-Request": "true",
            "HX-Trigger": "some-trigger",
            "HX-Target": "some-target",
            "HX-Current-URL": "http://testserver/calendar/week-view/"
        }

        cls.session_list = []
        for n in range(8, 18):
            session = SessionModel(
                client=cls.client_instance,
                date=cls.now.add(days=1).date(),
                start_time=p.time(n, 0),  # add one each hour
                end_time=p.time(n + 1, 0),  # Next week +1 hour
                calendar=cls.room_2,  # assuming you have cls.room_2 defined
                brief=f"Test{n}",
                fee=60,
                paid=False,
                attendance="LateC",
            )
            cls.session_list.append(session)
        SessionModel.objects.bulk_create(cls.session_list)


class CalendarOccurrenceTest(MetaTestSetupMixin, TestCase):

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
        self.assertTrue(form_valid_2.is_valid())  # testing form with two types of data

    def test_week_view_today_render(self):
        self.client.force_login(self.user)
        response = self.client.get('/calendar/week-view/')
        self.assertEqual(response.status_code, 200)
        expected_string = p.instance(self.session_1.end_time).format("H a")
        self.assertContains(response, expected_string)

    def test_week_view_today_render_htmx(self):
        self.client.force_login(self.user)
        expected_string = self.tenant.display_name
        response = self.client.post('/calendar/week-view/',
                                    self.calendar_data_2,
                                    follow=True,
                                    headers=self.htmx_headers)
        self.assertContains(response, expected_string)

    def test_week_dict_utils(self):
        sessions = SessionModel.objects.filter(date__week=self.now.week_of_year)
        calendar_render = CalendarRender(sessions, self.now)
        session = sessions[0]
        start_time = session.start_time
        week_day = session.date.isoweekday()
        self.assertEqual(calendar_render.week_dict[start_time][week_day], session)



    def test_render_views(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('room_calendar_app:week_view'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:room_calendar',args=[self.room_default.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:room_calendar_list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:room_calendar_manage'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:tenant',args=[self.tenant.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:tenant_list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:add_room_calendar'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:add_tenant'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:edit_room_calendar',args=[self.room_default.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('room_calendar_app:edit_tenant',args=[self.tenant.pk,]))
        self.assertEqual(response.status_code, 200)
