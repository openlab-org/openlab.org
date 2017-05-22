# python
import json
import random
import re

# django
from django.conf import settings
from django import template
from django.utils.translation import ugettext as _
from django.template import Context, Template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django.template import Library, Node, VariableDoesNotExist, Variable


register = template.Library()


@register.filter
def to_component_line_style(c, side):
    # for now, just randomize
    x = abs(hash(c.get('title'))) % 30 + 100
    y = abs(hash(c.get('summary'))) % 30 + 100

    s_template = """
        width: %(x)ipx;
        height: %(y)ipx;
    """
    s = s_template % {"x": x, "y": y}

    if side == "left":
        s += "top: 0; right: -%ipx;" % x
    else:
        s += "top: 0; left: -%ipx;" % x

    return s.replace("\n", "").replace("  ", "")

