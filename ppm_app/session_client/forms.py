from django import forms
from .models import Client,Session





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

class Switch(forms.Form):
    show_archive = forms.BooleanField(required=False,
                                label="Archived",
                                help_text="Show Archived",
                                widget=forms.CheckboxInput(attrs={
                                      "hx-post":"{% url 'session_client:client_list_all' %}",
                                        "hx-target":"#client-list-ul",
                                        "hx-swap":"innerHTML",
                                        "class":"form-check-input" 

                                })
                                )