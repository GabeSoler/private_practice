from django import forms 
from .models import Client,Session




class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code','nick_name','type','fee','motive','rel','goal','strategy']
        labels = {'code':'Code',                  
                  'nick_name':'Nickname',
                  'type':'Type',
                  'fee':'Fee',
                  'motive':'Motive',
                  'rel':'Relations',
                  'goal':'Goal',
                  'strategy':'Strategy'}
        widgets = {'motive':forms.Textarea(attrs={'cols':80}),
                   'rel':forms.Textarea(attrs={'cols':80}),
                   'goal':forms.Textarea(attrs={'cols':80}),
                   'strategy':forms.Textarea(attrs={'cols':80})}


class ClientSmallForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code','nick_name','type','fee']
        labels = {'code':'Code',                  
                  'nick_name':'Nickname',
                  'type':'Type',
                  'fee':'Fee',
        }

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

