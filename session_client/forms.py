from django import forms
from .models import ClientModel, SessionModel, ClientTimes
import pendulum as p
from base.choices import time_slot_options
from django.forms.widgets import DateInput, Select, SearchInput
from django.utils.translation import gettext_lazy as _

from .utils import time_plus_duration


class ClientForm(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code', 'type', 'fee', 'tenant', 'duration', 'active', 'link']
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
        fields = ['date', 'start_time']
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


class TimeAddForm(forms.ModelForm):
    class Meta:
        model = ClientTimes
        fields = ['tenant', 'day', 'time', 'client', 'fortnight']


class TimeEditForm(forms.ModelForm):
    class Meta:
        model = ClientTimes
        fields = ['tenant', 'day', 'time', 'fortnight']


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


class ClientAndMonthForSessions(forms.Form):
    clients = forms.ModelChoiceField(queryset=ClientModel.objects.all(), widget=forms.RadioSelect())
    dates = forms.DateField(widget=forms.Select(
        choices=[(p.now().subtract(months=1).start_of('month').to_date_string(),
                  p.now().subtract(months=1).start_of('month').format(
                      'MMM YYYY')),
                 (p.now().start_of('month').to_date_string(),
                  p.now().start_of('month').format('MMM YYYY')),
                 (p.now().add(months=1).start_of('month').to_date_string(),
                  p.now().add(months=1).start_of('month').format('MMM YYYY'))]))


from django.forms import BaseInlineFormSet
from django.db import models


class SessionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # example custom validation across forms in the formset
        for form in self.forms:
            # your custom formset validation
            start = form.cleaned_data['start_time']
            duration = form.instance.duration
            end = time_plus_duration(start, duration)
            form.cleaned_data['end_time'] = end
            date = form.cleaned_data['date']
            calendar = form.cleaned_data['tenant'].calendar
            qs = SessionModel.objects.filter(tenant__calendar=calendar, date=date).filter(
                models.Q(
                    start_time__gte=start,
                    start_time__lt=end,
                )
                | models.Q(
                    end_time__gt=start,
                    end_time__lte=end,
                )
                | models.Q(start_time__lt=start,
                           end_time__gt=end)
            )
            if qs:
                raise Exception("Session overlaps")
