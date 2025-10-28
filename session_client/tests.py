from django.test import TestCase
from django.urls import reverse

from room_calendar_app.tests import MetaTestSetupMixin
from session_client.models import SessionModel, ClientModel
import pendulum as p

from session_client.querysets import annotate_client_list


class TestClientSession(MetaTestSetupMixin,TestCase):
    def test_overlap_sessions(self):
        """ tests the first part of the system to check for overlaps """
        session = self.session_1
        session_overlap = self.session_overlap_1
        queryset = session.overlap_set()
        self.assertIn(session_overlap,queryset)
        self.assertEqual(len(queryset),1)



    def test_deduce_next_datetime(self):
        """ tests that the deduce function is calculating from client info """
        client = self.client_instance
        deduced_datetime = client.deduce_next_datetime()
        self.assertEqual(deduced_datetime.time(),client.time)
        self.assertEqual(deduced_datetime.isoweekday(),client.day)
        # I created a week later session in setup
        week = self.now.week_of_year + 1
        self.assertEqual(week,deduced_datetime.week_of_year)
        new_session = SessionModel(client=client)
        new_session.deduce_from_client(start_datetime=p.now().add(weeks=3))
        new_session.save()
        deduced_datetime = client.deduce_next_datetime()
        week = self.now.week_of_year + 3
        self.assertEqual(week,deduced_datetime.week_of_year)


    def test_deduce_from_client(self):
        """ check session can deduce room and dates from client info """
        building_session = SessionModel(client=self.client_instance)
        self.assertTrue(building_session.start_time,"09:00:00") #defaults
        self.assertTrue(building_session.end_time,"10:00:00") #defaults
        self.assertFalse(building_session.calendar)
        building_session.deduce_from_client()
        self.assertTrue(building_session.start_time,"08:00:00")
        self.assertTrue(building_session.end_time,"09:00:00")
        self.assertTrue(building_session.date,p.now().date())
        self.assertTrue(building_session.calendar,self.room_1)

    def test_is_unique_session(self):
        """ tests the overlap system is picking up one above and one bellow"""
        session = self.session_1
        session_overlap = self.session_overlap_1
        ok, overlaps = session.is_unique()
        self.assertFalse(ok)
        ok, overlaps = session_overlap.is_unique()
        self.assertFalse(ok)
        self.assertEqual(len(overlaps), 1)


    def test_series_overlap(self):
        client_instance = self.client_instance
        # creating a series to test overlaps with the defaults
        saved, new_series = client_instance.add_series(5,from_date=self.now.add(weeks=1))
        self.assertTrue(saved)
        self.assertEqual(len(new_series),5)
        # creating a session that lats for 9+ hours as clear overlap
        session = SessionModel(client=client_instance)
        session.deduce_from_client(start_datetime=p.now().add(weeks=1).at(8,0))
        session.end_time = session.end_time.add(hours=9) #range not picking up at all
        session.brief = "TestOverlap"
        session.save()
        # printing results to debug
        print("Overlap session start", session.start_time)
        print("Overlap session end", session.end_time)
        #The range to test
        start_range = self.now.subtract(weeks=5)
        end_range = self.now.add(weeks=5)
        #testing with only the calendar, range and day of the week
        overlaps = client_instance.check_series_overlap(start_range,end_range,
                                                      range_filter=True,
                                                        calendar_filter=True,
                                                        iso_day_filter=False,
                                                        time_filter=True)
        print("❗️Overlap list",overlaps)
        print("Series list",new_series)
        self.assertEqual(len(overlaps),5)


    def test_create_series(self):
        """ tests the series creation """
        client_instance = self.client_instance
        client_count = SessionModel.objects.filter(client=self.client_instance).count()
        client_instance.add_series(amount=5)
        client_count_after = SessionModel.objects.filter(client=self.client_instance).count()
        self.assertTrue(client_count<client_count_after)
        self.assertEqual(client_count_after-client_count,5)


    def test_create_session(self):
        ...
    def test_session_instance_modal(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:session_hx_item',
                                           args=(self.session_1.pk,)),
                                   headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,self.session_1.client)
        self.assertContains(response,self.session_1.brief)


    def test_annotate_client_list(self):
        clients = annotate_client_list(self.user,active=True)
        client = clients[0]
        self.assertEqual(len(clients),1)
        print("total_payments:",client.total_payments)
        self.assertEqual(client.total_payments,840)
        print("total_sessions:",client.total_sessions)
        self.assertEqual(client.total_sessions,14)
        print("month_sessions_paid:",client.month_sessions_paid)
        self.assertEqual(client.month_sessions_paid,60)
        print("month_sessions_expected:",client.month_sessions_expected)
        self.assertEqual(client.month_sessions_expected,180)
        print("pending_sort_sessions:",client.pending_sort_sessions)
        self.assertEqual(client.pending_sort_sessions,3)
        print("future_sessions_count:",client.future_sessions_count)
        self.assertEqual(client.future_sessions_count,11)
        print("month_sessions_count:",client.month_sessions_count)
        self.assertEqual(client.month_sessions_count,14)
        print("attendance_rate:",client.attendance_rate)
        self.assertEqual(client.attendance_rate,4/client.month_sessions_count)
        print("attendance_percentage:",client.attendance_percentage)
        self.assertAlmostEqual(client.attendance_percentage,client.attendance_rate * 100)


    def test_client_add_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:add_client'),headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"<form")
        self.assertContains(response,"<form")
        self.assertContains(response,self.room_1.name) #Blue
        self.assertContains(response,self.room_2.name) #Green
        self.assertContains(response,self.room_default.name) #Base Room
        self.client.logout()
        self.client.force_login(self.user_host)
        response = self.client.get(reverse('session_client:add_client'),headers=self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"<form")
        self.assertContains(response,"<form")
        self.assertNotContains(response,self.room_1.name) #Blue
        self.assertNotContains(response,self.room_2.name) #Green
        self.assertContains(response,self.room_default.name) #Base Room always needs to be there


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
        response = self.client.get(reverse('session_client:edit_client',args=[self.client_instance.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:client_hx_item',args=[self.client_instance.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_list_with_client',args=[self.client_instance.pk,]))
        self.assertEqual(response.status_code, 200)

    def test_render_session_views(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('session_client:session_view',args=[self.session_1.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_list_with_client',args=[self.client_instance.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_hx_item',args=[self.session_1.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_search'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:edit_session',args=[self.session_1.pk,]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('session_client:session_pending_list_modal',args=[self.client_instance.pk,]))
        self.assertEqual(response.status_code, 200)
