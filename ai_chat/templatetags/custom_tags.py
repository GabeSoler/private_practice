import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import bleach
register = template.Library()

@register.filter
@stringfilter
def markdown_format(value):
    md = markdown.Markdown(extensions=['tables'])
    md = md.convert(value)
    md = bleach.clean(md,tags={'a', 'abbr', 'acronym', 'b',
                               'blockquote', 'code', 'em',
                               'i', 'li', 'ol','p', 'strong',
                               'h1','h2','h3','h4','h5','h6',
                               'tr','td','th'})
    return mark_safe(md)
