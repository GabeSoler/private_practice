from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from room_calendar_app.tests import MetaTestSetupMixin
from session_client.models import SessionModel, ClientModel, ClientTimes
import pendulum as p

from session_client.querysets import annotate_client_list
from session_client.utils import time_plus_duration


class TestClientSession(MetaTestSetupMixin, TestCase):
    def test_annotate_client_list(self):
        clients = annotate_client_list(self.user)
        client = clients[0]
        sessions = client.sessionmodel_set.all()
        self.assertTrue(len(clients) > 0)
        self.assertTrue(len(sessions) > 0)
        self.assertEqual(len(clients), 2)
        print("total_payments:", client.total_payments)
        self.assertEqual(client.total_payments, 840)
        print("total_sessions:", client.total_sessions)
        self.assertEqual(client.total_sessions, 14)
        print("month_sessions_paid:", client.month_sessions_paid)
        self.assertEqual(client.month_sessions_paid, 60)
        print("month_sessions_expected:", client.month_sessions_expected)
        self.assertEqual(client.month_sessions_expected, 180)
        print("pending_sort_sessions:", client.pending_sort_sessions)
        self.assertEqual(client.pending_sort_sessions, 3)
        print("future_sessions_count:", client.future_sessions_count)
        self.assertEqual(client.future_sessions_count, 11)
        print("month_sessions_count:", client.month_sessions_count)
        sessions = client.sessionmodel_set.filter(date__month=self.now.month, )
        self.assertEqual(client.month_sessions_count, len(sessions))
        print("attendance_rate:", client.attendance_rate)
        three_month = SessionModel.objects.filter(client=client, date__range=(self.now.subtract(months=3).date(),
                                                                              self.now.date())).exclude(
            attendance="").count()
        three_month_attended = SessionModel.objects.filter(client=client,
                                                           date__range=(self.now.subtract(months=3).date(),
                                                                        self.now.date()), attendance="Attended").count()
        if three_month:
            attendance_rate = three_month_attended / three_month
            self.assertEqual(client.attendance_rate, attendance_rate)
            print("three_month:", three_month)
            print("three_month_attended:", three_month_attended)
        self.assertIsNotNone(client.attendance_rate)
        print("attendance_percentage:", client.attendance_percentage)
        self.assertAlmostEqual(client.attendance_percentage, client.attendance_rate * 100)

    def test_overlap_sessions(self):
        """ tests the first part of the system to check for overlaps """
        session = self.session_overlap_1
        session_overlap = self.session_overlap_2
        queryset = session.overlap_set()
        self.assertIn(session_overlap, queryset)
        self.assertEqual(len(queryset), 1)

    def test_get_last_date_or_now(self):
        """create a fresh client to set a first session on the past
            then create a session on the future to test the function
        """
        new_client = ClientModel.objects.create(
            user=self.user,
            code='test',
            tenant=self.tenant_default,
            duration=timedelta(hours=1)
        )
        SessionModel.objects.create(
            client=new_client,
            date=p.now().subtract(weeks=3).date(),
            start_time=p.time(8, 0),
            end_time=p.time(9, 30),
            tenant=self.tenant_default,

        )
        gotten_date = new_client.get_last_date_or_now()
        self.assertEqual(gotten_date.date(), self.now.date())

        # setting last date in the future
        future_session = SessionModel.objects.create(
            client=new_client,
            date=p.now().add(weeks=3).date(),
            start_time=p.time(8, 0),
            end_time=p.time(9, 30),
            tenant=self.tenant_default,
        )
        gotten_date = new_client.get_last_date_or_now()
        self.assertEqual(future_session.date, gotten_date.date())

    def test_deduce_next_datetime(self):
        """ tests that the deduce function is calculating from client info """
        client = self.client_instance
        session_date = self.now.add(weeks=20).next(p.FRIDAY).date()
        session = SessionModel.objects.create(client=client,
                                              tenant=self.tenant_default,
                                              date=session_date,
                                              start_time="09:00",
                                              end_time=time_plus_duration("09:00", client.duration)
                                              )
        deduced_datetime = client.deduce_next_datetime()
        self.assertEqual(deduced_datetime.day_of_week, p.MONDAY)
        # the deduced time should be a week later
        self.assertEqual(deduced_datetime.subtract(weeks=1).week_of_year, session_date.week_of_year)
        session.date = p.instance(session.date).next(p.TUESDAY)
        session.save()
        self.assertEqual(deduced_datetime.subtract(weeks=1).week_of_year, session_date.week_of_year)
        new_client = ClientModel.objects.create(code="NEW", tenant=self.tenant_default,
                                                duration=timedelta(hours=1),
                                                user=self.user
                                                )
        session.client = new_client
        session.date = p.instance(session.date).next(p.THURSDAY)
        session_date = session.date
        session.save()
        deduced_datetime = new_client.deduce_next_datetime()
        # the deduced day must match the client day
        self.assertEqual(deduced_datetime.day_of_week, session_date.day_of_week)
        # the deduced time should be a week later
        self.assertEqual(deduced_datetime.subtract(weeks=1).week_of_year, session_date.week_of_year)

    def test_deduce_from_client(self):
        """ check session can deduce room and dates from client info """
        client = self.client_instance
        client_time = self.client_instance_time_1
        building_session = SessionModel(client=client)
        self.assertEqual(building_session.start_time, "09:00:00")  # defaults
        self.assertEqual(building_session.end_time, "10:00:00")  # defaults
        self.assertFalse(building_session.tenant)
        building_session.deduce_from_client()
        self.assertEqual(building_session.start_time, client_time.time)  # it to defaults of client
        building_session.start_time = p.time(12, 0)
        building_session.deduce_from_client(start_time=False)
        self.assertNotEqual(building_session.start_time, client_time.time)  # needs to update and set bellow endtime
        self.assertEqual(building_session.end_time, time_plus_duration(client_time.time, client.duration))  # defaults
        self.assertEqual(building_session.tenant, client_time.tenant)
        self.assertEqual(building_session.date, client.deduce_next_datetime().date())
        self.assertEqual(building_session.tenant.calendar, self.room_1)

    def test_is_unique_session(self):
        """ tests the overlap system is picking up one above and one bellow"""
        session = self.session_overlap_1
        session_overlap = self.session_overlap_1
        ok, overlaps = session.is_unique()
        self.assertFalse(ok)
        ok, overlaps = session_overlap.is_unique()
        self.assertFalse(ok)
        self.assertEqual(len(overlaps), 1)

    def test_series_overlap(self):
        client_instance = self.client_instance
        # creating a series to test overlaps with the defaults
        saved, series = client_instance.add_series(5, add_weeks=2,
                                                   overlap_check=False)
        self.assertTrue(saved)
        self.assertEqual(len(series), 5)

        # creating overlaps with a new client
        new_client = ClientModel(tenant=self.tenant,
                                 user=self.user,
                                 duration=p.duration(hours=1),
                                 code="NewClient!",
                                 )
        new_client.save()
        client_time = ClientTimes.objects.create(client=new_client,
                                                 time="08:00:00",
                                                 tenant=self.tenant,
                                                 day=p.FRIDAY,
                                                 fortnight=False)
        new_saved, new_series = new_client.add_series(5, add_weeks=2,
                                                      overlap_check=False)
        self.assertTrue(new_saved)
        self.assertEqual(len(new_series), 5)
        date_of_new_session = p.instance(new_series[0].date)
        self.assertEqual(date_of_new_session.day_of_week, client_time.day)
        # The range to test
        start_range = self.now.add(weeks=2)
        end_range = self.now.add(weeks=9)
        # testing with only the calendar, range and day of the week
        overlaps = self.client_instance_time_1.check_series_overlap(start_range, end_range)
        overlaps_2 = client_time.check_series_overlap(start_range, end_range)
        print(f"* Series list,old {series}")
        print(f"* Series list,new {new_series}")
        print("* ❗️Overlap list", overlaps)
        self.assertEqual(len(overlaps), 5)
        self.assertEqual(len(overlaps_2), 5)

    def test_create_series(self):
        """ tests the series creation """
        client_instance = self.client_instance
        client_count = SessionModel.objects.filter(client=self.client_instance).count()
        client_instance.add_series(5)
        client_count_after = SessionModel.objects.filter(client=self.client_instance).count()
        self.assertTrue(client_count < client_count_after)
        self.assertEqual(client_count_after - client_count, 5)

    def test_create_session(self):
        ...

    def test_session_instance_modal(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:session_hx_item',
                                           args=(self.session_1.uuid,)),
                                   headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session_1.client)
        self.assertContains(response, self.session_1.keywords)

    def test_client_add_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:add_client'), headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertContains(response, self.tenant)
        self.assertNotContains(response, self.tenant_host)
        self.assertContains(response, f"{self.user.username}</option>")
        self.client.logout()
        response = self.client.get(reverse('session_client:add_client'))
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user_host)
        response = self.client.get(reverse('session_client:add_client'), headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertIsNotNone(self.user_host)
        self.assertIsNotNone(self.tenant_host)
        self.assertNotContains(response, self.tenant)
        self.assertContains(response, f"{self.user_host.username}</option>")
        self.assertNotContains(response, f"{self.user.username}</option>")
        self.assertContains(response, self.tenant_host)

    def test_render_client_views(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:client_list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:add_client'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:client_archived'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:client_search'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:edit_client', args=[self.client_instance.uuid, ]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:client_hx_item', args=[self.client_instance.uuid, ]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('session_client:session_list_with_client', args=[self.client_instance.uuid, ]))
        self.assertEqual(response.status_code, 200)

    def test_render_session_views(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('session_client:session_list_with_client', args=[self.client_instance.uuid, ]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_hx_item', args=[self.session_1.uuid, ]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_search'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:edit_session', args=[self.session_1.uuid, ]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('session_client:session_pending_list_modal', args=[self.client_instance.uuid, ]))
        self.assertEqual(response.status_code, 200)

    def test_extra_times_client_method(self):
        client = self.client_instance
        extra_time_1 = client.add_time(p.MONDAY, p.time(10, 30))
        extra_time_2 = client.add_time(p.TUESDAY, p.time(10, 30))
        self.assertTrue(isinstance(extra_time_1, ClientTimes))
        self.assertEqual(3, client.times.count())
        created, sessions = client.add_series(3)
        self.assertTrue(created)
        self.assertEqual(len(sessions), 9)

    def test_sessions_add_in_month(self):
        """ Test gives the view son basic testing
        still misses some more specific checks
        """
        import json
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:sessions_add_in_month'))
        self.assertEqual(response.status_code, 200)
        headers = {
            "HX-Request": "true",
            "HX-Trigger": "id_client",
            "HX-Trigger-Name": "client",
            "HX-Target": "session-list-form",
            "HX-Current-URL": reverse("session_client:sessions_add_in_month"),
            "Triggering-Event": json.dumps({
                "type": "RefreshTable",
            }),
        }
        data = {'date': p.now().date(), 'client': self.client_instance.pk, 'time': p.now().time()}
        response = self.client.post(reverse('session_client:sessions_add_in_month'), data, headers=headers)
        self.assertEqual(response.status_code, 200)
        headers = {
            "HX-Request": "true",
            "HX-Trigger": "id_client",
            "HX-Trigger-Name": "client",
            "HX-Target": "session-list-form",
            "HX-Current-URL": reverse("session_client:sessions_add_in_month"),
            "Triggering-Event": json.dumps({
                "type": "submit",
            }),
        }
        data = {'date': p.now().date(), 'client': self.client_instance.pk, 'time': p.now().time()}
        response = self.client.post(reverse('session_client:sessions_add_in_month'), data, headers=headers)
        self.assertEqual(response.status_code, 200)
