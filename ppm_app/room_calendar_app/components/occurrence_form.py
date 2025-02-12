from django_unicorn.components import UnicornView
from ..forms import OccurrenceUnicornForm
from ..models import Event,OccurrenceModel
from ..choices import time_slots,duration_times
from datetime import datetime,timedelta
from django.utils import timezone

class OccurrenceFormView(UnicornView):
    form_class = OccurrenceUnicornForm
    event = Event.objects.none()
    event_select = Event.objects.none()
    time_slot_options = time_slots()
    duration_times = duration_times()
    start_date = ""
    start_time = ""
    duration = ""

    def mount(self):
        self.event_select = Event.objects.filter(user=self.request.user)

    def save_occurrence(self):
        start_datetime = datetime.combine(date=self.start_date,time=self.start_time)
        event = self.event
        end_time = start_datetime + self.duration
        if self.is_valid:
            occurrence = OccurrenceModel.objects.create(
                                         start_time=start_datetime,
                                         end_time=end_time,
                                         duration=self.duration,
                                         event=event)
            occurrence.save()
            self.reset()
            return
        else:
            return
        

    def user_occurrences(self):
        hour = timezone.now() - timedelta(hours=2)
        user_occurrences = OccurrenceModel.objects.filter(event__user=self.request.user,created_at__gte=hour)
        return user_occurrences
