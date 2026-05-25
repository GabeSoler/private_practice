from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

class RoomCalendarAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "room_calendar_app"

    def ready(self):
        from . import signals
        post_save.connect(signals.signal_setup_room_calendar,sender=get_user_model())
