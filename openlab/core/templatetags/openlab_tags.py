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
def get_at(obj, index):
    """ Simple way to quickly resolve a variable in a template """
    return obj[index]


@register.filter
def first_half(value):
    """
    Only returns first half of list
    """
    if not value:
        return []
    return value[:int(len(value)/2)]

@register.filter
def second_half(value):
    """
    Only returns second half of list
    """
    return value[int(len(value)/2):]

@register.filter
def first_of(value, arg=10):
    """
    Only returns first X of list
    """
    if not value:
        return value
    count = int(arg)
    if len(value) > arg:
        return value[:arg]
    else:
        return value


@register.filter
def label_bytes(b):
    try:
        b = float(b)
    except ValueError:
        return b

    #if b >= 1099511627776:
    #    terab = b / 1099511627776
    #    size = '%.2fT' % terab
    if b == 0:
        return "0"

    if b >= 1073741824:
        gigab = b / 1073741824
        size = '%.2fG' % gigab
    elif b >= 1048576:
        megab = b / 1048576
        size = '%.2fM' % megab
    elif b >= 1024:
        kilob = b / 1024
        size = '%.2fK' % kilob
    else:
        size = '%.2fb' % b
    return size


@register.filter
def classname(value, options=''):
    """
    Returns classname.

    If options is given, checks if class name is in there before returning,
    else it returns None.
    """
    cn = value.__class__.__name__.lower()
    if not options or cn in options:
        return cn
    return ''



@register.filter
def users_to_json(value):
    """
    Serializes a list of users as JSON
    """
    lst = []
    for user in value:
        lst.append({
                'username': user.username,
                'desired_name': user.profile.desired_name,
            })
    return json.dumps(lst)


CHARS = re.compile(r'[\W_-]+')
@register.filter
def beautify(value):
    return CHARS.sub(' ', value).strip().capitalize()


@register.filter
def to_json(d):
    """
    Serializes a give dict
    """
    return json.dumps(d)


@register.filter
def endswith(d, v):
    # ugh
    choices = v.split(",")
    for choice in choices:
        if d.endswith(choice):
            return True
    return False



##############################################################
# Switch statement from https://djangosnippets.org/snippets/967/

@register.tag(name="switch")
def do_switch(parser, token):
    """ 
    The ``{% switch %}`` tag compares a variable against one or more values in 
    ``{% case %}`` tags, and outputs the contents of the matching block.  An 
    optional ``{% else %}`` tag sets off the default output if no matches 
    could be found:: 

        {% switch result_count %} 
            {% case 0 %} 
                There are no search results.  
            {% case 1 %} 
                There is one search result.  
            {% else %} 
                Jackpot! Your search found {{ result_count }} results.  
        {% endswitch %} 

    Each ``{% case %}`` tag can take multiple values to compare the variable 
    against:: 

        {% switch username %} 
            {% case "Jim" "Bob" "Joe" %} 
                Me old mate {{ username }}! How ya doin?  
            {% else %} 
                Hello {{ username }} 
        {% endswitch %} 
    """ 
    bits = token.contents.split() 
    tag_name = bits[0] 
    if len(bits) != 2: 
        raise template.TemplateSyntaxError("'%s' tag requires one argument" % tag_name) 
    variable = parser.compile_filter(bits[1]) 

    class BlockTagList(object): 
        # This is a bit of a hack, as it embeds knowledge of the behaviour 
        # of Parser.parse() relating to the "parse_until" argument.  
        def __init__(self, *names): 
            self.names = set(names) 
        def __contains__(self, token_contents): 
            name = token_contents.split()[0] 
            return name in self.names 

    # Skip over everything before the first {% case %} tag 
    parser.parse(BlockTagList('case', 'endswitch')) 

    cases = [] 
    token = parser.next_token() 
    got_case = False 
    got_else = False 
    while token.contents != 'endswitch': 
        nodelist = parser.parse(BlockTagList('case', 'else', 'endswitch')) 
        
        if got_else: 
            raise template.TemplateSyntaxError("'else' must be last tag in '%s'." % tag_name) 

        contents = token.contents.split() 
        token_name, token_args = contents[0], contents[1:] 
        
        if token_name == 'case': 
            tests = list(map(parser.compile_filter, token_args)) 
            case = (tests, nodelist) 
            got_case = True 
        else: 
            # The {% else %} tag 
            case = (None, nodelist) 
            got_else = True 
        cases.append(case) 
        token = parser.next_token() 

    if not got_case: 
        raise template.TemplateSyntaxError("'%s' must have at least one 'case'." % tag_name) 

    return SwitchNode(variable, cases) 

class SwitchNode(Node): 
    def __init__(self, variable, cases): 
        self.variable = variable 
        self.cases = cases 

    def __repr__(self): 
        return "<Switch node>" 

    def __iter__(self): 
        for tests, nodelist in self.cases: 
            for node in nodelist: 
                yield node 

    def get_nodes_by_type(self, nodetype): 
        nodes = [] 
        if isinstance(self, nodetype): 
            nodes.append(self) 
        for tests, nodelist in self.cases: 
            nodes.extend(nodelist.get_nodes_by_type(nodetype)) 
        return nodes 

    def render(self, context): 
        try: 
            value_missing = False 
            value = self.variable.resolve(context, True) 
        except VariableDoesNotExist: 
            no_value = True 
            value_missing = None 
        
        for tests, nodelist in self.cases: 
            if tests is None: 
                return nodelist.render(context) 
            elif not value_missing: 
                for test in tests: 
                    test_value = test.resolve(context, True) 
                    if value == test_value: 
                        return nodelist.render(context) 
        else: 
            return "" 


# http://stackoverflow.com/questions/1070398/how-to-set-a-value-of-a-variable-inside-a-template-code
class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name
    def render(self, context):
        context[self.var_name] = self.new_val
        return ''

@register.tag
def setvar(parser,token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    new_val, var_name = m.groups()
    if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SetVarNode(new_val[1:-1], var_name)


