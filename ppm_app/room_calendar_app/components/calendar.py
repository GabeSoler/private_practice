from django_unicorn.components import UnicornView
from ..models import Event,OccurrenceModel,RoomCalendarModel
from django.utils.timezone import now

class CalendarView(UnicornView):
    event = Event.objects.last()
    occurrences = OccurrenceModel.objects.all()
    user = None
    #calendars = RoomCalendarModel.objects.all()

    def mount(self):
        self.user = self.component_kwargs["user"]

    def occurrences(self):
        """ you can access supposedly as values"""
        pass

    def calendars(self):
        """ you can access supposedly as values"""
        return RoomCalendarModel.objects.filter(user=self.user)
