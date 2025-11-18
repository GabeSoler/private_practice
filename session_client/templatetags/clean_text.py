from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import bleach
import markdown

register = template.Library()

@register.filter
@stringfilter
def bleach_me(value):
    bleached = bleach.clean(value,tags={'abbr', 'acronym',
                               'blockquote', 'code', 'em','b',
                                'p', 'strong',
                               })
    return mark_safe(bleached)

@register.filter
@stringfilter
def markdown_format(value):
    md = markdown.Markdown(extensions=['tables'],output_format='html')
    md = md.convert(value)
    md = bleach.clean(md,tags={'a', 'abbr', 'acronym', 'b',
                               'blockquote', 'code', 'em',
                               'i', 'li', 'ol','p', 'strong',
                               'h1','h2','h3','h4','h5','h6',
                               'tr','td','th','br'})
    return mark_safe(md)

@register.filter
@stringfilter
def markdown_emphasis(value):
    md = markdown.Markdown(output_format='html')
    md = md.convert(value)
    md = bleach.clean(md,tags={'b',
                               'blockquote', 'code', 'em',
                               'i','ul', 'li', 'ol','p', 'strong',
                               'br'})
    return mark_safe(md)
