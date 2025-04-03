from django import forms
from .models import Client,Session





class ClientForm(forms.ModelForm):
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