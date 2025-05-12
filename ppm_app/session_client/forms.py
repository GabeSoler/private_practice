from django import forms
from .models import Client,Session
from django.utils import timezone
import pendulum as p



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code','type','fee']
        labels = {'code':'Code',                  
                  'type':'Type',
                  'fee':'Fee',
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title','session_date','client','notes','paid','attended']
        labels = {'title':'Title',
                  'session_date':'Date',
                  'client':'Client',
                  'notes':'Session Note',
                  'paid':'Confirm payment',
                  'attended':'Record attendance'}
        field_classes = {
            "session_date":forms.SplitDateTimeField,
        }
        widgets = {'notes':forms.Textarea(attrs={'cols':80}),
                   'session_date':forms.SplitDateTimeWidget(date_attrs={'class':'form-select','type':'date'},
                                                            time_attrs={'class':'form-select','type':'time'},
                                                            date_format="%Y-%m-%d",
                                                            time_format="%H:%M",
                                                            )}

class SessionShortForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title','client']
        labels = {'title':'Title',
                  'client':'Client'
        }

class SearchSessionFrom(forms.Form):
    date_ref_start = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now().subtract(months=1))
    date_ref_end = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=p.now())
    client = forms.ModelChoiceField(queryset=Client.objects.all(),required=False)

class SearchClientForm(forms.Form):
    search_input = forms.CharField(max_length=20,required=True,help_text="type client code")
    active = forms.BooleanField(help_text="Search Archived",initial=True,required=False,
                                widget=forms.CheckboxInput(attrs={'class':'form-check-input','type':"checkbox",'role':'switch'}))