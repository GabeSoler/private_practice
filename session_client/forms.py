from django import forms
from .models import ClientModel,SessionModel
import pendulum as p
from session_client.widgets import SelectSplitDateTime
from session_client.choices import time_slot_options
from django.utils import timezone

class ClientForm(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code','nick_name','type','fee','room_calendar','day','duration','active']
        labels = {'code':'Code',                  
                  'type':'Type',
                  'fee':'Fee',
                  'nick_name':'Nickname',
                  'room_calendar':'Room',
                  'day':'Default Day',
                  'duration':'Duration',
                  'active':'Active',
        }

class ClientFormShort(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code','day','duration','time']
        labels = {'code':'Code',                  
                  'day':'Default Day',
                  'time':'time',
                  'duration':'Duration',
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['title','start_datetime','client','notes','paid','amount_paid','attended']
        labels = {'title':'Title',
                  'start_datetime':'Date',
                  'client':'Client',
                  'notes':'Session Note',
                  'paid':'Confirm payment',
                  'amount_paid':'Confirm amount',
                  'attended':'Record attendance'}
        # I needed to add the split field so it processes date and time before goes to DateTime
        field_classes = {
            "start_datetime":forms.SplitDateTimeField,
        }
        # I custom made Select split datetime, so I can restrict time options for then rendering the calendar
        widgets = {'notes':forms.Textarea(attrs={'cols':80}),
                   'start_datetime':SelectSplitDateTime(date_attrs={'class':'form-select','type':'date'},
                                                            time_attrs={'class':'form-select','type':'time'},
                                                            date_format="%Y-%m-%d",
                                                            time_choices=time_slot_options
                                                            )}




class SessionShortForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['start_datetime','client']
        labels = {'start_datetime':'Day and Time',
                  'client':'Client'
        }
        field_classes = {
            "start_datetime":forms.SplitDateTimeField,
        }
        # I custom made Select split datetime, so I can restrict time options for then rendering the calendar
        widgets = {'notes':forms.Textarea(attrs={'cols':80}),
                   'start_datetime':SelectSplitDateTime(date_attrs={'class':'form-select','type':'date'},
                                                            time_attrs={'class':'form-select','type':'time'},
                                                            date_format="%Y-%m-%d",
                                                            time_choices=time_slot_options
                                                            )}


# class SessionShortForm(forms.ModelForm):
#     class Meta:
#         model = SessionModel
#         fields = ['title','client']
#         labels = {'title':'Title',
#                   'client':'Client'
#         }

class SearchSessionFrom(forms.Form):
    date_ref_start = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now().subtract(months=1))
    date_ref_end = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now())
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(),required=False)

class SearchClientForm(forms.Form):
    search_input = forms.CharField(max_length=20,required=True,help_text="type client code")
    active = forms.BooleanField(help_text="Search Archived",initial=True,required=False,
                                widget=forms.CheckboxInput(attrs={'class':'form-check-input','type':"checkbox",'role':'switch'}))