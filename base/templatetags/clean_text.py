from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import bleach
import markdown

register = template.Library()

@register.filter
@stringfilter
def bleach_me(value):
    bleached = bleach.clean(value)
    return mark_safe(bleached)

@register.filter
@stringfilter
def markdown_format(value):
    """ formats text into Markdown
    gives you full freedom of action with it
    danger with titles as it breaks design
    """
    md = markdown.Markdown(extensions=['smarty','nl2br','tables','attr_list',
                                       'sane_lists','md_in_html','fenced_code'],
                           output_format='html')
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
    """ allows using Markdown to give emphasis to text
    blocks the titles and other options that would disrupt the design
    """
    md = markdown.Markdown(output_format='html',
                           extensions=['smarty','nl2br','attr_list','sane_lists','fenced_code'])
    md = md.convert(value)
    md = bleach.clean(md,tags={
                               'blockquote', 'code', 'em',
                               'i','ul', 'li', 'ol','p', 'strong','b',
                               'br'})
    return mark_safe(md)
