from django import forms
from .models import DeleteAccount
from .widgets.turnstile import TurnstileField
from decouple import config
from allauth.account.forms import SignupForm, LoginForm


class DeleteAccountForm(forms.ModelForm):
    """a form before deleting account"""

    class Meta:
        model = DeleteAccount
        fields = ('reason', 'confirm')
        labels = {
            'reason': 'Please select a reason:',
            'confirm': 'Please confirm delete, all your data will be erased.'
        }
        widgets = {
            'reason': forms.RadioSelect,
            'confirm': forms.CheckboxInput,
        }


import sys


class MyCustomSignupForm(SignupForm):
    if 'test' in sys.argv:  # I am sending a different form when in testing, to avoid conflicts
        turnstile_field = forms.CharField(max_length=8, required=False)
    else:
        turnstile_field = TurnstileField(secret_key=config('TURNSTILE_SECRET_KEY'),
                                         site_key=config('TURNSTILE_SITE_KEY'))


class MyCustomLoginForm(LoginForm):
    if 'test' in sys.argv:
        turnstile_field = forms.CharField(max_length=8, required=False)
    else:
        turnstile_field = TurnstileField(secret_key=config('TURNSTILE_SECRET_KEY'),
                                         site_key=config('TURNSTILE_SITE_KEY'))
