from django.test import TestCase
from room_calendar_app.tests import MetaTestSetupMixin
from session_client.models import SessionModel

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
        week = self.now.week_of_year + 1
        self.assertEqual(week,deduced_datetime.week_of_year)
        deduced_datetime = client.deduce_next_datetime(add_weeks=3)
        week = self.now.week_of_year + 3
        self.assertEqual(week,deduced_datetime.week_of_year)


    def test_deduce_from_client(self):
        """ checks session can deduce room and dates from client info """
        building_session = SessionModel(client=self.client_instance)
        self.assertFalse(building_session.start_datetime)
        self.assertFalse(building_session.end_datetime)
        self.assertFalse(building_session.calendar)
        building_session.deduce_from_client()
        self.assertTrue(building_session.start_datetime)
        self.assertTrue(building_session.end_datetime)
        self.assertTrue(building_session.calendar)

    def test_is_unique_session(self):
        """ tests the overlap system is picking up one above and one bellow"""
        session = self.session_1
        session_overlap = self.session_overlap_1
        ok, overlaps = session.is_unique()
        self.assertFalse(ok)
        ok, overlaps = session_overlap.is_unique()
        self.assertFalse(ok)
        self.assertEqual(len(overlaps), 1)
