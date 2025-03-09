from django.forms.widgets import DateInput

class DateBooted(DateInput):
    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx['widget']['type'] = "date"
        ctx['widget']['attrs']['class'] = "form-control"
        return ctx
    