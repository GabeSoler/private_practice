from django_unicorn.components import UnicornView
from ..models import Event,OccurrenceModel,RoomCalendarModel
from django.utils import timezone
from ..choices import time_slots


class CalendarView(UnicornView):
    event = Event.objects.none()
    calendars = RoomCalendarModel.objects.none()

    def mount(self):
        self.user = self.request.user

    def occurrences(self):
        today = timezone.now().date()
        week = today.isocalendar().week
        week = OccurrenceModel.objects.filter(start_time__week=week).order_by("start_time")
        return week
    
    def week_dict(self):
        week_dict = {}
        occurrences = self.occurrences()
        for slot in time_slots():
            week_dict[slot] = {}
            for i in range(1,8):
                weekday = {i:object}
                week_dict[slot].update(weekday)
        for slot,day in week_dict.items():
            for d,_ in day.items():
                iso_day = int(d)
                input = occurrences.filter(start_time__time=slot, start_time__iso_week_day=iso_day)
                week_dict[slot][iso_day] = input
        return week_dict


    def calendars(self):
        """ you can access supposedly as values"""
        return RoomCalendarModel.objects.filter(user=self.user)
