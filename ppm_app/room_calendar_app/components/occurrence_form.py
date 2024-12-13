from django_unicorn.components import UnicornView
from ..models import OccurrenceModel,Event
from ..choices import default_timeslot_options

class OccurrenceFormView(UnicornView):
    form_class = OccurrenceModel
    start_time = ""
    duration = ""
    event = ""
    event_select = None
    def mount(self):
        self.event_select = Event.objects.filter(user=self.request.user)
        start_date = ""
        start_hour = ""
        time_slot_options = default_timeslot_options
    def save_occurrence(self):
        if self.is_valid:
            OccurrenceModel.objects.create(user=self.request.user,
                                         start_time=self.start_time,
                                         duration=self.duration,
                                         event=self.event)
            self.reset()