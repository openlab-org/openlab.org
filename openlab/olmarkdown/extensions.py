# md
import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree

# django
from openlab.users.models import User

from django.template.loader import render_to_string
from django.utils import html

# 1st party
from openlab.gallery.models import Photo
from openlab.hubpath.models import hubpath_objects


class BaseObjectLinkPattern(Pattern):
    """
    Object Link, possibly within a given context.

    Example:
    @jane     - user named jane
    #123      - task number
    :asdf.stl - file
    !123      - photo at 123
    """
    # For example {{ :123 }}
    REGEX = r'\{\{\s*(%s)%s(%s+)\s*([a-z ]*)\s*\}\}'
    PATH_REGEX_REQUIRED = r'\w[\w-]*/\w[\w-]*'
    PATH_REGEX_OPTIONAL = r'[\w-]*/?[\w-]*'
    IDENT = r'\d'

    has_pathspec = True

    def handleMatch(self, m):
        if self.has_pathspec:
            # Full info
            path_spec = m.group(2)
            identifier = m.group(3)
            args = [a.strip() for a in m.group(4).split() if a.strip()]
        else:
            # Singular info
            identifier = m.group(2)
            path_spec = ''
            args = []

        el = self.make_el(self.object_context, path_spec, identifier, args)
        return el

    @classmethod
    def make_el(cls, object_context, path_spec, identity, args=[]):
        if not object_context:
            # need to look up object_context
            object_context = hubpath_objects.get(path_spec)

        s = cls.render_template({
                'object': object_context,
                #'path': path_spec,
                'id': identity,
                'args': args,
            })
        el = etree.fromstring(s)
        return el

    @classmethod
    def update_context(cls, ctx):
        return ctx

    @classmethod
    def get_regex(cls, abs_only=False):
        """
        Create regexp for this pattern
        """
        #spec = cls.PATH_REGEX_REQUIRED if abs_only else cls.PATH_REGEX_OPTIONAL

        # Note:  "abs_only" is disabled
        spec = cls.PATH_REGEX_OPTIONAL
        re_str = cls.REGEX % (spec, cls.SIGIL, cls.IDENT)
        return re_str

    @classmethod
    def make(cls, obj):
        me = cls(cls.get_regex(bool(obj)))
        me.object_context = obj
        return me

    @classmethod
    def render_template(cls, ctx):
        ctx = cls.update_context(ctx)
        obj = ctx.get('object')
        ctx.update({
                'class_name': cls.name,
                'context_class_name': obj.__class__.__name__.lower(),
            })
        s = render_to_string('olmarkdown/tag/%s.html' % cls.name, ctx).strip()
        # clean up output
        s = html.strip_spaces_between_tags(s)
        return s

####
# Non ProjectObjectLink ones:
# {{ reply 1342  }}  (reply to comment with that ID)
# @user_name         (reference given user)


class ReplyPattern(BaseObjectLinkPattern):
    """
    Matches
    !123
    """
    name = r'reply'
    REGEX = r'\{\{\s*reply\s+(\d+)\s*([a-z ]*)\s*\}\}'

    @classmethod
    def get_regex(cls, abs_only=False):
        """
        Create regexp for this pattern
        """
        return cls.REGEX


class UserPattern(BaseObjectLinkPattern):
    """
    Matches
    !123
    """
    name = r'user'
    REGEX = r'@(\w+)'
    has_pathspec = False
    CLUE_ATTR = 'data-olmd-username-mention'

    @classmethod
    def get_regex(cls, abs_only=False):
        """
        Create regexp for this pattern
        """
        return cls.REGEX

    @classmethod
    def update_context(cls, ctx):
        ctx['username'] = ctx['id']
        try:
            ctx['user'] = User.objects.get(username=ctx['id'])
        except User.DoesNotExist:
            ctx['user'] = None
        else:
            ctx['clue'] = cls.CLUE_ATTR + ("='%s'" % ctx['username'])
        return ctx


# How markdown presently works:
# 1. Markdown is "object independent". Will not worry about broken links for
# now. Much simpler.
# 2. "MarkdownAble" base class for InfoBase to derive from
# 3. Specify how to get the object context ahead of time
# 4. Apply Markdown on every object on save(), also store split version with
# HTML stripped
#
# THUS, we shouldn't worry about writing slow templates as I am here, just
# import from XHTML rendered using normal templates.

class PhotoPattern(BaseObjectLinkPattern):
    """
    Matches
    !123
    """
    SIGIL = r'!'
    name = r'photo'

    @classmethod
    def update_context(cls, ctx):
        obj = ctx['object']
        identity = ctx['id']
        ctx['photo'] = Photo.objects.get(gallery=obj.gallery, number=identity)
        return ctx


class TicketPattern(BaseObjectLinkPattern):
    """
    Matches
    #123
    """
    SIGIL = r'#'
    name = r'ticket'

    @classmethod
    def update_context(cls, ctx):
        obj = ctx['object']
        identity = ctx['id']
        ctx['ticket'] = Ticket.objects.get(ticketmaster=obj.ticketmaster,
                                                number=identity)
        return ctx



class FilePattern(BaseObjectLinkPattern):
    """
    Matches
    :file.txt
    """
    SIGIL = r':'
    IDENT = r'[\w\.-]'
    name = r'file'

    @classmethod
    def update_context(cls, ctx):
        obj = ctx['object']
        identity = ctx['id']
        ctx['ticket'] = FileModel.objects.get(project=obj, path=identity)
        return ctx



# Supported formats:
# {{ user/project#137 }}       (ticket for project)
# {{ user/project:asdf.stl }}  (embed file for project)
# Assume current project:
# {{ #137 }}                   (ticket for current project)
# {{ :asdf.stl }}              (embed file for project)
# {{ !13 }}                    (Photo for current project)
# {{ :asdf.stl link }}         (embed a link to a file for a project)


class ObjectLinkExtension(markdown.Extension):
    PATTERNS = [
            ('ol_photo',  PhotoPattern),
            ('ol_ticket', TicketPattern),
            ('ol_file',   FilePattern),
            ('ol_reply',  ReplyPattern),
            ('ol_user',   UserPattern),
        ]

    def __init__(self, object_context):
        self.object_context = object_context
        super(ObjectLinkExtension, self).__init__()

    def extendMarkdown(self, md, md_globals):
        # Insert instance of 'mypattern' before 'references' pattern
        patterns = [(k, c.make(self.object_context)) for k, c in self.PATTERNS]

        # Disable built in markdown image stuff
        del md.inlinePatterns['image_link']
        del md.inlinePatterns['image_reference']

        for k, pattern in patterns:
            #md.inlinePatterns.add(k, pattern, '>entity')
            md.inlinePatterns.add(k, pattern, '_end')


BASE_EXTENSIONS = ['smart_strong', 'sane_lists', 'tables', 'codehilite', 'def_list']

def markdown_creator_for_object(obj):
    # Make this "instantialize" for page with a given context, then all
    # subsequent markdown calls are done within that context (much faster
    # templates)
    md = markdown.Markdown()
    return md



def markdown_for_object(text, obj):
    # TODO maybe use bleach instead?
    e = BASE_EXTENSIONS + [ObjectLinkExtension(obj)]
    return markdown.markdown(text, extensions=e,
                        safe_mode='escape')

