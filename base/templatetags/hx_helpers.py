from django import template
from base.choices import ATTENDANCE
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def attendance_choices_as_html():
    """ links attendance options to the choices library to help htmx rendering"""
    html = ''
    for name,display in ATTENDANCE:
        html += f'<option value="{name}">{display}</option>'
    return mark_safe(html)
