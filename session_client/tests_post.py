from django.test import TestCase
from django.urls import reverse
from room_calendar_app.tests import MetaTestSetupMixin
from session_client.models import ClientModel, SessionModel
import pendulum as p
from django.utils import translation
from datetime import timedelta
from .forms import (ClientForm,
                    SearchClientForm,
                    SessionFromCalendarForm,
                    SessionSelectGroupForm)


class PostMethodTests(MetaTestSetupMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        user_language = "en"
        translation.activate(user_language)

    def test_client_search_view_post(self):
        url = reverse('session_client:client_search')
        # Search for 'Session1' which is session_1.keywords
        data = {'search_input': "session", 'client': ""}
        form = SearchClientForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "session")

    def test_add_client_view_post(self):
        url = reverse('session_client:add_client')
        data = {
            'code': 'NEWCLIENT',
            'type': 'Private',
            'fee': 50,
            'tenant': self.tenant.pk,
            'day': 1,
            'time': "10:00:00",
            'duration': timedelta(hours=1, minutes=30),
            'series': '1',
            'active': 'True',
        }
        form = ClientForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)  # Returns HttpResponseClientRefresh
        self.assertNotContains(response, "<form")
        self.assertTrue(ClientModel.objects.filter(user=self.user, code='NEWCLIENT').exists())

    def test_edit_client_view_post(self):
        url = reverse('session_client:edit_client', args=[self.client_instance.pk])
        data = {
            'code': 'UPDATEDCODE',
            'type': 'Private',
            'fee': 70,
            'tenant': self.tenant.pk,
            'day': 2,
            'time': '11:00:00',
            'duration': timedelta(minutes=30),
            'series': '2',
            'active': 'False',
        }
        form = ClientForm(data=data)
        print(form.errors)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.client_instance.refresh_from_db()
        self.assertEqual(self.client_instance.code, 'UPDATEDCODE')

    def test_week_view_add_session_post(self):
        url = reverse('session_client:week_view_add_client', kwargs={'weekday': 1, 'time': '08:00'})
        date_ref = p.now().format('YYYY-MM-DD')
        data = {
            "client": self.client_instance.pk,
            "date": date_ref,
            "start_time": "08:00:00",
            "calendar": self.room_1.pk,
        }
        form = SessionFromCalendarForm(data=data)
        if form.errors:
            print(form.errors)
        self.assertTrue(form.is_valid())

        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SessionModel.objects.filter(client=self.client_instance, date=date_ref).exists())

    def test_sessions_view_post_htmx(self):
        url = reverse('session_client:session_list')
        data = {
            'only_unpaid': False,
            'include_next': False,
        }
        form = SessionSelectGroupForm(data=data)
        self.assertTrue(form.is_valid())
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertNotContains(response, self.client_instance_2.code)  # to check a form clients query
        self.assertEqual(response.status_code, 200)
        # Check if one of the sessions is present
        self.assertNotContains(response, f"id_{self.session_2.pk}")
        data['only_unpaid'] = True
        data['include_next'] = True
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"id_{self.session_2.pk}")
        self.assertNotContains(response, 'hx-post="/en/clients/session_list/"')  # check not form passed
        # testing client filter
        data['client'] = self.client_instance_3.pk
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertNotContains(response, f"id_{self.session_2.pk}")

    def test_sessions_search_post(self):
        url = reverse('session_client:session_search')
        data = {
            'date_ref_start': (p.now().subtract(months=1)).format('YYYY-MM-DD'),
            'date_ref_end': (p.now().add(months=1)).format('YYYY-MM-DD'),
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"id_{self.session_1.pk}")
        self.assertContains(response, f"id_{self.session_2.pk}")
        data_2 = {
            'date_ref_start': (p.now().subtract(days=1)).format('YYYY-MM-DD'),
            'date_ref_end': (p.now().add(days=1)).format('YYYY-MM-DD'),
        }
        response = self.client.post(url, data_2, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"id_{self.session_1.pk}")
        self.assertNotContains(response, f"id_{self.session_2.pk}")

    def test_add_session_view_post(self):
        url = reverse('session_client:add_session')
        data = {
            'date': p.now().add(days=2).format('YYYY-MM-DD'),
            'start_time': '14:00',
            'client': self.client_instance.pk,
            'fee': 60,
            'open': True,
            'calendar': self.room_1.pk,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SessionModel.objects.filter(client=self.client_instance, start_time='14:00:00').exists())

    def test_edit_session_view_post(self):
        url = reverse('session_client:edit_session', args=[self.session_1.pk])
        data = {
            'keywords': 'UPDATEDBRIEF',
            'date': self.session_1.date.strftime('%Y-%m-%d'),
            'start_time': self.session_1.start_time.strftime('%H:%M'),
            'client': self.session_1.client.pk,
            'fee': 100,
            'open': True,
            'calendar': self.session_1.calendar.pk,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.session_1.refresh_from_db()
        self.assertEqual(self.session_1.keywords, 'UPDATEDBRIEF')

    def test_week_view_add_session_client_post(self):
        url = reverse('session_client:week_view_add_session_client', kwargs={
            'year': p.now().year,
            'week': p.now().week_of_year,
            'week_day': 1,
            'time': '15:00'
        })
        data = {
            'client': self.client_instance.pk,
            'date': p.now().format('YYYY-MM-DD'),
            'start_time': '15:00',
            'calendar': self.room_1.pk,
            'fee': 60,
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(SessionModel.objects.filter(client=self.client_instance, start_time='15:00:00').exists())
        self.assertNotContains(response, f"id_client_helptext")

    def test_sessions_patch_attendance_post(self):
        url = reverse('session_client:session_patch_attendance', args=[self.session_1.pk])
        data = {
            'attendance': 'LateC'
        }
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.session_1.refresh_from_db()
        self.assertEqual(self.session_1.attendance, 'LateC')
        self.assertContains(response, 'LateC')

    def test_patch_brief_view_post(self):
        url = reverse('session_client:session_patch_brief', args=[self.session_1.pk])
        data = {'keywords': 'NEW NOTES'}
        response = self.client.post(url, data, headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.session_1.refresh_from_db()
        self.assertEqual(self.session_1.keywords, 'NEW NOTES')
