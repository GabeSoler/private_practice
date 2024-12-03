from django_unicorn.components import UnicornView
from models import Event


class EventListView(UnicornView):
    user = None
    model = Event
    events = Event.objects.filter(user=user)

    def mount(self):
        user_mount = self.request.user
        self.user = user_mount
        events = events


         
