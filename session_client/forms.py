from django import forms
from .models import ClientModel, SessionModel, ClientTimes
import pendulum as p
from base.choices import time_slot_options
from django.forms.widgets import DateInput, Select, SearchInput
from django.utils.translation import gettext_lazy as _


class ClientForm(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code', 'type', 'fee', 'tenant', 'duration', 'series', 'active', 'link']
        labels = {'code': _('Code'),
                  'type': _('Type'),
                  'fee': _('Fee'),
                  'tenant': _('Tenant'),
                  'duration': _('Duration'),
                  'active': _('Active'),
                  'link': _('Link'),
                  }
        widgets = {'active': forms.CheckboxInput(
            attrs={'class': 'form-check-input', "type": "checkbox", "role": "switch", 'name': "radioDefault"}),
        }


class ClientFormShort(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code', 'duration', ]
        labels = {'code': _('Code'),
                  'duration': _('Duration'),
                  }


class SessionForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['keywords', 'date', 'start_time', 'client', 'paid', 'fee', 'attendance', 'open', 'tenant']
        labels = {
            'keywords': _('Keywords'),
            'date': _('Date'),
            'start_time': _('time'),
            'client': _('Client'),
            'paid': _('Paid'),
            'fee': _('Amount'),
            'open': _('Open'),
            'attendance': _('Attendance'),
            'tenant': _('Tenant'),
        }
        # I needed to add the split field so it processes date and time before goes to DateTime
        widgets = {'date': forms.DateInput(attrs={'class': 'form-select', 'type': 'date'},
                                           format="%Y-%m-%d"),
                   'start_time': forms.Select(attrs={'class': 'form-select'},
                                              choices=time_slot_options,
                                              ),
                   'paid': forms.CheckboxInput(
                       attrs={'class': 'form-check-input', 'type': "checkbox", 'role': 'switch'}),
                   'open': forms.CheckboxInput(
                       attrs={'class': 'form-check-input', 'type': "checkbox", 'role': 'switch'}),
                   }


class SessionShortForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['date', 'start_time', 'client']
        labels = {
            'start_time': _('Day and Time'),
            'client': _('Client'),
        }
        widgets = {'date': DateInput(attrs={'class': 'form-select', 'type': 'date'},
                                     format="%Y-%m-%d"),
                   'start_time': Select(attrs={'class': 'form-select', 'type': 'time'},
                                        choices=time_slot_options)}


class SessionFromCalendarForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['client', 'date', 'start_time', 'tenant']
        widgets = {'date': forms.DateInput(attrs={'class': 'form-select', 'type': 'date'},
                                           )}


class StartDateSessionForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['start_time']
        labels = {'start_time': _('Day and Time')}


class SessionSelectGroupForm(forms.Form):
    """ for changin open sessions """
    only_unpaid = forms.BooleanField(required=False, label="Only Unpaid")
    include_next = forms.BooleanField(required=False, label="Include Next")
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(), required=False)


class SearchSessionForm(forms.Form):
    """ for session search by date and client """
    date_ref_start = forms.DateField(widget=forms.DateInput(attrs={"type": "date", }), required=True,
                                     initial=p.now().subtract(months=1))
    date_ref_end = forms.DateField(widget=forms.DateInput(attrs={"type": "date", }), required=True,
                                   initial=p.now().add(weeks=1))
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(), required=False)


class SearchClientForm(forms.Form):
    """ to search for clients """
    search_input = forms.CharField(max_length=100, required=True, help_text="type text search")
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(), required=False, help_text="Select Client")
    widgets = {"search_input": SearchInput}


class SelectAttendanceForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['attendance']


class PatchBriefForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['keywords']


class ClientFromCalendarForm(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code', 'duration', 'fee', 'type', 'tenant']


class TimeForm(forms.ModelForm):
    class Meta:
        model = ClientTimes
        fields = ['tenant', 'day', 'time', 'client', 'fortnight']


class SessionsBulkActionsForm(forms.Form):
    actions = forms.ChoiceField(widget=forms.Select, required=True,
                                choices=(
                                    ("None", "---"),
                                    ("open", "Set as Open"),
                                    ("close", "Set as Close"),
                                    ("attended", "Set as Attended"),
                                    ("paid", "Set as Paid"),
                                    ("unpaid", "Set as Unpaid"),
                                ))
