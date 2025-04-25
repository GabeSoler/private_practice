from django import forms
from .models import Client,Session
from django.utils import timezone




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
        fields = ['title','client','notes','paid','attended']
        labels = {'title':'Title',
                  'client':'Client',
                  'notes':'Session Note',
                  'paid':'Confirm payment',
                  'attended':'Record attendance'}
        widgets = {'notes':forms.Textarea(attrs={'cols':80})}

class SessionShortForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title','client']
        labels = {'title':'Title',
                  'client':'Client'
        }

class SearchSessionFrom(forms.Form):
    date_reference = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=timezone.now())
    client = forms.ModelChoiceField(queryset=Session.objects.all())