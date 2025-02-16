from django.forms.widgets import Input

class DateBooted(Input):
    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx['widget']['type'] = "date"
        ctx['widget']['attrs']['class'] = "form-control"
        return ctx
    