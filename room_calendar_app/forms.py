from django import forms

from .models import RoomCalendarModel,TenantModel
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
        fields = ("name","description")
        labels = {
            "name":"Your name to display",
            "description":"a description of the place you are linking to",
        }

class LinkTenantForm(forms.Form):
    tenant_id = forms.UUIDField(required=True,label='Tenant Code',help_text='Paste here')



class WeekCalendarForm(forms.Form):
    """calendar switch form"""
    date_reference = forms.DateField(widget=forms.DateInput(attrs={"type":"date",}),required=True,initial=timezone.now(),
                                     help_text='Select week reference')
    calendar = forms.ModelChoiceField(queryset=RoomCalendarModel.objects.all(),required=False, help_text='Select the calendar to search')

