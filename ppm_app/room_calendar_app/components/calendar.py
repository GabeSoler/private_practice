from django_unicorn.components import UnicornView
from ..models import Event,OccurrenceModel,RoomCalendarModel
from django.utils import timezone
from calendar_utils import week_dict_occ,week_days
class CalendarView(UnicornView):
    user = None
    event = Event.objects.none()
    calendars = RoomCalendarModel.objects.none()
    now = timezone.now()
    week_days_display = []
    week_dict_display = {}
    
    def mount(self):
        self.user = self.request.user
        self.week_dic_display = week_dict_occ(self.occurrences())
        self.week_days_display = week_days(date=self.now)

    def occurrences(self):
        today = self.now
        week = today.isocalendar().week
        week = OccurrenceModel.objects.filter(start_time__week=week).order_by("start_time")
        return week
    

    def calendars(self):
        """ you can access supposedly as values"""
        return RoomCalendarModel.objects.filter(user=self.user)
