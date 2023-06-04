from markdown import markdown

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render(value):
    """Render markdown to html"""
    raw_content = escape(value)
    html_content = markdown(raw_content)
    return mark_safe(html_content)
