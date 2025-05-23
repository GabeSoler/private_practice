from django.forms import MultiWidget
from django.forms.widgets import DateInput,Select
from django.forms.utils import to_current_timezone

class SelectSplitDateTime(MultiWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """

    supports_microseconds = False
    template_name = "django/forms/widgets/splitdatetime.html"

    def __init__(
        self,
        attrs=None,
        date_format=None,
        date_attrs=None,
        time_attrs=None,
        time_choices=None,
    ):
        widgets = (
            DateInput(
                attrs=attrs if date_attrs is None else date_attrs,
                format=date_format,
            ),
            Select(
                attrs=attrs if time_attrs is None else time_attrs,
                choices=time_choices,
            ),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time()]
        return [None, None]
