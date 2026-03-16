from django.forms import Field
from django.forms.widgets import TextInput
from django.core.exceptions import ValidationError
import requests
from urllib.error import HTTPError
import json


class TurnstileWidget(TextInput):
    template_name = 'accounts/widgets/turnstile.html'
    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return data.get('cf-turnstile-response')


class TurnstileField(Field):
    default_error_messages = {
        'error_turnstile': 'Turnstile could not be verified.',
        'invalid_turnstile': 'Turnstile could not be verified.',
        'required': 'Please prove you are a human.',
    }
    def __init__(self, secret_key, site_key):
        self.secret_key = secret_key
        self.site_key = site_key
        self.widget = TurnstileWidget(attrs={'key':self.site_key})
        super().__init__()


    def validate(self,value):
        super().validate(value)
        post_data = {
            'secret': self.secret_key,
            'response': value,
        }

        response_data = self._try_turnstile(post_data)

        if not response_data['success']:
            raise ValidationError(self.error_messages['invalid_turnstile'], code='invalid_turnstile')

    def _try_turnstile(self, post_data:dict):
        try:
            response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify",json=post_data)
        except HTTPError:
            raise ValidationError(self.error_messages['error_turnstile'], code='error_turnstile')
        return json.loads(response.content)
