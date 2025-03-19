from django import forms
from .my_widgets import DateBooted

from .models import RoomCalendarModel,Event,TenantModel,OccurrenceModel
from .choices import default_timeslot_options,duration_times_as_choices
from django.utils import timezone


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
    tenant_id = forms.UUIDField(required=True,label='Tenant Code',help_text='Ask for it to another user')

class EventForm(forms.ModelForm):
    """Event form"""
    class Meta:
        model = Event
        fields = ("client","room_calendar",
                  "title","description","event_type",)
        labels = {
            "client":"Client?",
            "room_calendar":"Room",
            "title":"Title",
            "description":"Description",
            "event_type":"Type",
        }


class OccurrenceForm(forms.ModelForm): #! not in use
    """ occurrence form """
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
    start_date = forms.DateField(widget=DateBooted, label="On")
    start_time = forms.TimeField(label="At",widget=forms.Select(choices=default_timeslot_options))
    duration = forms.DurationField(label="For",widget=forms.Select(choices=duration_times_as_choices))


class WeekCalendarForm(forms.Form):
    """calendar switch form"""
    date = forms.DateTimeField(widget=DateBooted,initial=timezone.now())
    calendar = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all(),required=False)

