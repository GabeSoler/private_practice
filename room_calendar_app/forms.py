from random import choices

from django import forms

from session_client.choices import MONTH_SHORT, years_choices
from .models import RoomCalendarModel, TenantModel, BlocksModel
from django.utils import timezone


class RoomCalendarForm(forms.ModelForm):
    class Meta:
        model = RoomCalendarModel
        fields = ("name","description","percentage","cost")
        labels = {
        "name" : "Name",
        "description" : "Description",
            "percentage" : "Percentage charge",
            "cost" : "Cost of per session",
        }

class TenantForm(forms.ModelForm):
    class Meta:
        model = TenantModel
        fields = ("display_name","name","description")
        labels = {
            "display_name":"Your name to display",
            "name":"Name for your records",
            "description":"a description of the place you are linking to",
        }

class LinkTenantForm(forms.Form):
    tenant_id = forms.UUIDField(required=True,label='Tenant Code',help_text='Paste here')



class WeekCalendarForm(forms.Form):
    """calendar switch form"""
    date_reference = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=timezone.now(),
                                     help_text='Select week reference')
    calendar = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all(),required=False, help_text='Select the calendar to search')


class RoomReportForm(forms.Form):
    room = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all())
    month = forms.ChoiceField(choices=MONTH_SHORT)
    year = forms.ChoiceField(choices=years_choices())

class TenantReportForm(forms.Form):
    month = forms.ChoiceField(choices=MONTH_SHORT)
    year = forms.ChoiceField(choices=years_choices())

class RoomSwitchForm(forms.Form):
    room = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all())

class BlockForm(forms.ModelForm):
    class Meta:
        model= BlocksModel
        fields = ['tenant','start_time','end_time','day']
