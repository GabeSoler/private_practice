from django import forms
from django.forms.utils import to_current_timezone
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import SelectDateWidget

from .models import *
from .choices import *

class MultipleIntegerField(forms.MultipleChoiceField):
    """
    A form field for handling multiple integers.

    """

    def __init__(self, choices, size=None, label=None, widget=None):
        widget = widget or forms.SelectMultiple(attrs={"size": size or len(choices)})
        super().__init__(
            required=False,
            choices=choices,
            label=label,
            widget=widget,
        )

    def clean(self, value):
        return [int(i) for i in super().clean(value)]


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


    
class EventForm(forms.ModelForm):
    """
    A simple form for adding and updating Event attributes

    """

    class Meta:
        model = Event
        fields = ("client","room_calendar",
                  "title","description","event_type",)
        labels = {
            "client":"",
            "room_calendar":"",
            "title":"",
            "description":"",
            "event_type":"",
        }

    def __init__(self, *args, **kwargs):
      	# Extract the user from the view
        user = kwargs.pop('user')
        super(Client, self).__init__(*args, **kwargs)
        # Filter authors related to the logged-in user
        self.fields['client'].queryset = Client.objects.filter(user=user)
        self.fields['room_calendar'].queryset = RoomCalendarModel(tenants__contain=user)

class SingleOccurrenceForm(forms.ModelForm):
    """
    A simple form for adding and updating single Occurrence attributes

    """

    start_time = forms.SplitDateTimeField(widget=SplitDateTimeWidget)
    end_time = forms.SplitDateTimeField(widget=SplitDateTimeWidget)

    class Meta:
        model = OccurrenceModel
        fields = "__all__"
