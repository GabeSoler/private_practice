from django import forms
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


from .models import *
from .choices import *


class MultipleOccurrenceForm(forms.ModelForm):
    class Meta:
        model = MultiOccurrenceModel
        fields = ("day_start","start_time","end_time",
                  "until","frequency","interval",
                  "week_days_1","week_days_2","week_days_3",
                  "month_option","month_ordinal",
                  "month_ordinal_day","each_month_day",)
        labels = {
                "day_start":"Day to start the recurrence",
                "start_time":"Time to sto start",
                "end_time":"Time to end",
                # recurrence options
                "until":"Date when to stop repeating",
                "frequency":"Please mark if daily, weekly or monthly",
                "interval":"How often to repeat(2 = every other time)",
                # weekly options
                "week_days_1":"Select which day of the week",
                "week_days_2":"A second day on same week (optional)",
                "week_days_3":"A third day on same week (optional)",
                # monthly options
                "month_option":"select which type of monthly repeat",
                "month_ordinal":"Which week of every month",
                "month_ordinal_day":"Which weekday on week selected",
                "each_month_day":"Which day of every month",
                    }


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
    class Meta:
        model = OccurrenceModel
        fields = ("start_time","duration","event")
        labels = {"start_time":"Time to start (please select 15 min increments)",
                  "duration":"how long",
                  "event":"Attach an event (ie a client)"}
        widgets = {
            "start_time":forms.SplitDateTimeWidget(
                                                    date_format='%Y-%m-%d',
                                                    time_format="%a %m %y",
                                                    date_attrs={"type":"date"},
                                                    time_attrs={"type":"time","max":"21:00","min":"08:00","step":"900"}
                                                    )}

