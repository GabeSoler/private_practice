from django import forms
from .models import ClientModel,SessionModel
import pendulum as p
from session_client.widgets import SelectSplitDateTime
from session_client.choices import time_slot_options
from django.forms.widgets import DateInput,Select

class ClientForm(forms.ModelForm):
    class Meta:
        model = ClientModel
        fields = ['code','nick_name','type','fee', 'calendar', 'day','time', 'duration','series', 'active']
        labels = {'code':'Code',                  
                  'type':'Type',
                  'fee':'Fee',
                  'nick_name':'Nickname',
                  'calendar': 'Room',
                  'day':'Default Day',
                  'duration':'Duration',
                  'active':'Active',
                  }
        widgets = {'active':forms.CheckboxInput(attrs={'class':'form-check-input',"type":"checkbox", "role":"switch", 'name':"radioDefault"}),
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
        fields = ['brief','date','start_time', 'client', 'paid', 'amount_paid', 'attended','open','calendar']
        labels = {'brief':'Brief',
                  'date': 'Date',
                  'start_time': 'time',
                  'client':'Client',
                  'paid':'Paid',
                  'amount_paid':'Amount',
                  'open':'Open',
                  'attended':'Attendance'}
        # I needed to add the split field so it processes date and time before goes to DateTime
        widgets = {'date':forms.DateInput(attrs={'class': 'form-select', 'type': 'date'},
                                                    format="%Y-%m-%d"),
                   'start_time':forms.Select(attrs={'class':'form-select'},
                                                    choices=time_slot_options,
                                             ),
                   'brief':forms.Textarea(attrs={'class':'form-control','rows':3}),
                   'paid':forms.CheckboxInput(attrs={'class':'form-check-input','type':"checkbox",'role':'switch'}),
                   'open':forms.CheckboxInput(attrs={'class':'form-check-input','type':"checkbox",'role':'switch'}),
                   }





class SessionShortForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['date','start_time', 'client']
        labels = {'start_time': 'Day and Time',
                  'client':'Client'
                  }
        widgets = {'date':DateInput(attrs={'class': 'form-select', 'type': 'date'},
                                                    format="%Y-%m-%d"),
                   'start_time':Select(attrs={'class':'form-select','type':'time'},
                                                    choices=time_slot_options)}
class SessionFromOnlyClientForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['client']

class StartDateSessionForm(forms.ModelForm):
    class Meta:
        model = SessionModel
        fields = ['start_time']
        labels = {'start_time': 'Day and Time'}

class SessionSelectGroupForm(forms.Form):
    only_unpaid = forms.BooleanField(required=False,label="Only Unpaid")
    include_next = forms.BooleanField(required=False,label="Include Next")
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(),required=False,label="Client")

class SearchSessionFrom(forms.Form):
    date_ref_start = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now().subtract(months=1))
    date_ref_end = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now())
    client = forms.ModelChoiceField(queryset=ClientModel.objects.all(),required=False)

class SearchClientForm(forms.Form):
    search_input = forms.CharField(max_length=20,required=True,help_text="type client code")
    active = forms.BooleanField(help_text="Search Archived",initial=True,required=False,
                                widget=forms.CheckboxInput(attrs={'class':'form-check-input','type':"checkbox",'role':'switch'}))