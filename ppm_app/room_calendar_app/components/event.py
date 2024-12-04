from django_unicorn.components import UnicornView
from forms import EventForm

class EventView(UnicornView):
    form_class = EventForm
    
    def mount(self):
        form = EventForm

    def add_event(self):
        if self.is_valid():
            self.save()
            