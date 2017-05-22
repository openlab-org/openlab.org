from django import template
from django.utils.safestring import mark_safe

from .. import extensions

register = template.Library()

@register.filter
def olmarkdown(value, obj):
    """
    Wraps given text with OpenLab Markdown.

    Obj should be one of (for context):
    * Project, Team, Service
        Adds extensions based on a project, ie for project wikipages, tasks, photos, etc
    * User
        Creates extensions based on user, ie for a user's profile or a comment
        on a user's action
    """
    result = extensions.markdown_for_object(value, obj)
    # return mark_safe(result) # Was causing tests to fail
    return str(mark_safe(result))

