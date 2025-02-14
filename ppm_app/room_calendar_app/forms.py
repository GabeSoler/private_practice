from django import forms
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.forms.widgets import SelectDateWidget


from .models import *
from .choices import *


class RoomCalendarForm(forms.ModelForm):
    class Meta:
        model = RoomCalendarModel
        fields = ("name","description")
        labels = {
        "name" : "Name of your Room Calendar",
        "description" : "Describe your place",
        }

class TenantForm(forms.ModelForm):
    class Meta:
        model = TenantModel
        fields = ("name","description")
        labels = {
            "name":"Your name to display",
            "description":"a description of the place you are linking to",
        }

class LinkTenantForm(forms.Form):
    tenant_id = forms.UUIDField(required=True)

class EventForm(forms.ModelForm):
    """Event form"""
    class Meta:
        model = Event
        fields = ("client","room_calendar",
                  "title","description","event_type",)
        labels = {
            "client":"It there a client associated?(optional)",
            "room_calendar":"Which room it belongs to?",
            "title":"Give it a memorable title",
            "description":"What it is about?",
            "event_type":"Select a type of event",
        }


class OccurrenceForm(forms.ModelForm):
    """ occurrence form """
    start_time = forms.SplitDateTimeField()
    class Meta:
        model = OccurrenceModel
        fields = ("start_time","duration","event")
        labels = {"start_time":"Time to start (please select 15 min increments)",
                  "duration":"how long",
                  "event":"Attach an event (ie a client)"}
        widgets = {
            "start_time":forms.SplitDateTimeWidget(
                                                    date_format="%Y-%m-%d",
                                                    time_format="%a %m %y",
                                                    date_attrs={"type":"date"},
                                                    time_attrs={"type":"time","max":"21:00","min":"08:00","step":"900"}
                                                    )}


class OccurrenceProxyForm(forms.Form):
    """ occurrence form """
    start_date = forms.DateField()
    start_time = forms.TimeField(input_formats='H:i')
    duration = forms.DurationField()
    event = forms.ModelChoiceField(queryset=Event.objects.all())


class WeekCalendarView(forms.Form):
    """calendar switch form"""
    date = forms.DateField()
    calendar = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all())



class SplitDateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into a SelectDateWidget for dates and
    Select widget for times.

    """

    def __init__(self, attrs=None):
        widgets = (
            SelectDateWidget(attrs=attrs),
            forms.Select(choices=default_timeslot_options, attrs=attrs),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]