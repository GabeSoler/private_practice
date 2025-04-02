from django import forms 
from .models import Client,Session




class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code','nick_name','type','fee','motive','rel','goal','strategy']
        labels = {'code':'Add a code identifier for your clients(connected to your contact details system)',                  
                  'nick_name':'Give a Nick Name',
                  'type':'Chose a client type',
                  'fee':'Agreed fee',
                  'motive':'Clients motive for consulting',
                  'rel':'Relational context of client',
                  'goal':'Agreed goal(s) for therapy',
                  'strategy':'Your first thoughts for how to approach the process'}
        widgets = {'motive':forms.Textarea(attrs={'cols':80}),
                   'rel':forms.Textarea(attrs={'cols':80}),
                   'goal':forms.Textarea(attrs={'cols':80}),
                   'strategy':forms.Textarea(attrs={'cols':80})}


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title','client','notes','paid','attended']
        labels = {'title':'Give an overall title to the session',
                  'client':'Link session to a client',
                  'notes':'Brief and descriptive note of session',
                  'paid':'Confirm payment',
                  'attended':'Record attendance'}
        widgets = {'notes':forms.Textarea(attrs={'cols':80})}
