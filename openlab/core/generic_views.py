"""
View class hierarchy is based here.

These classes are the root of a massive class hierarchy that gives things like
breadcrumbs on every page, properly working tabs, implied permission checks,
etc.

The view class hierarchy mirrors the model class hierarchy. Main objects in
Open Lab (Project, Team, and eventually Service) all descend from "InfoBase".
Likewise, their views descend from the Info view.  This allows for sharing code
to do things like manage users in a project and manage users in a team,
changing properties / forms, uploading media, etc

Examples:

Info
 |
 v
ProjectInfo

Info
 |
 v
Wiki
 |
 v
ProjectWiki
"""



# django
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe, mark_for_escaping
from django.middleware.csrf import get_token
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib import messages

# 3rd party
from cities_light.models import Country, Region, City, to_search
from actstream.actions import is_following, follow, unfollow
from actstream import registry

# 1st party
from openlab.gallery.models import  Photo
from openlab.accounts.forms import make_manage_user_forms_context,\
                    make_manage_user_access_forms_context

# local
from .generic_view_exceptions import *
import collections


def _one_of(val, *options):
    assert not val or val in options or val.strip('-') in options
    return val or options[0]


from django.conf.urls import url
def url_helper(regexp, view, url_name_suffix=''):
    """
    Quick helper function that constructs a URL name, such as:
        team_followers, team_members, etc
    Or, in the case of manage functions:
        team_manage_edit, team_manage_members
    """
    url_name = view.get_url_name() + url_name_suffix
    return url(regexp, view.as_view(), {}, url_name)


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class IsActive(object):
    """
    Helper class to include in context to render views properly
    """
    IS_ACTIVE_ATTR = 'class="active"'
    IS_ACTIVE_CLASS = 'active'
    def __init__(self, active, on_match=None):
        self.active = str(active).strip().lower()
        self.string = on_match or self.IS_ACTIVE_ATTR

    def __getitem__(self, name):
        if str(name).strip() == self.active:
            s = mark_safe(self.string)
            s.as_class = self.IS_ACTIVE_CLASS
            return s
        return ''


class Info(View):
    """
    For InfoBase objects
    """
    parent_view = None

    def get(self, request, *args, **kwargs):
        try:
            ctx = self.get_context_data(request)
        except ResponseExceptionBase as e:
            return e.response

        self.add_breadcrumbs(request, ctx)
        return render(request, self.get_template_name(), ctx)


    def add_breadcrumbs(self, request, ctx):


        ##########################
        # Breadcrumbs
        v = self.parent_view
        # make list, then loop over list backward
        lst = []
        while v:
            bc = v.breadcrumb(ctx) if isinstance(v.breadcrumb, collections.Callable) else v.breadcrumb
            lst.append((bc, v.get_reverse_url(self)))
            v = v.parent_view

        lst.reverse()

        for a in lst:
            request.breadcrumbs(*a)

        # Add breadcrumb for current page
        bc = self.breadcrumb(ctx) if isinstance(self.breadcrumb, collections.Callable) else self.breadcrumb
        request.breadcrumbs(bc, request.path)
        ##########################

        # add self
        ctx['page_title'] = bc


    def get_context_data(self, request):
        return {}

    def get_template_name(self):
        maybe = lambda s: getattr(self, s) if hasattr(self, s) else ''
        return ''.join([maybe('template_prefix'),
                maybe('template_interfix'),
                maybe('template_basename'),
                '.html'])

    def redirect_parent_view(self):
        return redirect(self.parent_view.get_reverse_url(self))

    @classmethod
    def get_url_name(cls):
        s = "%s_%s" % (cls.noun, cls.template_basename)
        return s

    @classmethod
    def get_reverse_url(cls, other_view):
        return reverse(cls.get_url_name())



#######################################
# Project details views

class ViewInfo(Info):
    template_interfix = "view/"
    action = None
    can_edit = None
    varname = None

    def post(self, request, *a, **k):
        self.action = request.POST.get('action')
        # sanity check
        #assert self.action in self.actions

        if self.action == 'forking':
            # Actually forking request
            return self.handle_forking(request)

        return self.get(request, *a, **k)

    def get_object(self, request):
        """
        Gets the object in question.
        """
        field = self.kwargs.get(self.field)
        k = { self.field: field }
        obj = get_object_or_404(self.model, **k)
        return obj

    def check_permission(self, request, ctx):
        # Later we'll want to add a permission check for viewing objects for
        # private teams or projects
        pass

    def handle_following(self, user, obj):
        if not user.is_authenticated():
            return False

        registry.register(obj.__class__) # TODO remove this
        following = is_following(user, obj)

        if self.action == 'follow_toggle':
            # Toggle follow!
            [follow, unfollow][int(following)](user, obj)

            # toggle what we return
            following = not following

        return following

    def handle_forking(self, request):
        if not request.user.is_authenticated():
            # shouldn't happen
            return False

        obj = self.get_object(request)
        args = self.get_forking_args(request)
        new_obj = obj.fork(*args)
        return redirect(new_obj.get_absolute_url())


    def get_context_data(self, request):
        # Get the object that we're viewing
        obj = self.get_object(request)

        following = self.handle_following(request.user, obj)

        c = {
                'obj': obj,
                'object_class': self.model_class,
                'is_following': following,
                'actions_available': self.actions,
                self.varname or self.noun: obj,
            }

        if self.can_edit:
            c['can_edit'] = self.can_edit(obj, request.user)
        else:
            c['can_edit'] = obj.editable_by(request.user)

        if self.template_interfix.startswith('view') or\
                self.template_interfix.startswith('update'):
            # In viewing ones
            c['tab'] = IsActive(self.template_basename)
        else:
            # In editing ones
            c['tab'] = IsActive('manage')
            c['tab_manage'] = IsActive(self.template_basename)

        c.update(self.get_core_context(request, obj))
        c.update(self.get_more_context(request, obj))

        # Check to see if we can view (or modify the object)
        self.check_permission(request, c)

        return c

    @classmethod
    def get_reverse_url(cls, other_view):
        arg = other_view.kwargs.get(cls.field)
        return reverse(cls.get_url_name(), args=(arg,))

    def get_more_context(self, request, obj):
        return {}

    def get_core_context(self, request, obj):
        return {}




class ViewOverviewInfo(ViewInfo):
    template_basename = "about"

    @classmethod
    def get_url_name(cls):
        """
        For the initial view, just go with bare noun
        """
        return cls.noun

    @classmethod
    def breadcrumb(cls, ctx):
        """
        For breadcrumbs, use the string representation of the current object.
        """
        return str(ctx.get('obj'))


class ViewActivityInfo(ViewInfo):
    template_basename = "activity"
    breadcrumb = _('Activity')


class ViewMembersInfo(ViewInfo):
    # For Team, its pageable list of members. For 
    template_basename = "members"
    breadcrumb = _('Members')

    def get_more_context(self, request, obj):
        c = {}
        all_types = { 'owner': [obj.user] }
        for field_name in self.member_field_names:
            # later add in paging if necessary
            c[field_name] = getattr(obj, field_name).all()
            all_types[field_name] = c[field_name]

        c['member_types'] = all_types

        return c





##########################################
# Browsing interface

class ListInfo(Info):
    template_interfix = "browse/"
    template_basename = "list"
    PAGE_SIZE = 40

    def get_context_data(self, request, arg=1):
        ordering = '-updated_date'

        # Fetch tags
        #tags = self.model.tags.most_common()
        page_number = request.GET.get('page', self.kwargs.get('page', 1))

        search = {}

        if 'tag' in request.GET:
            search['tag'] = str(request.GET['tag'])

        if 'q' in request.GET:
            search['search_terms'] = str(request.GET['q']).split()

        if 'country' in self.kwargs:
            # country codes are all uppercase in DB, lowercase in URL
            country_code = str(self.kwargs['country']).upper()
            country  = Country.objects.filter(code2=country_code)
            search['country'] = country and country[0]

        #if request.GET.get('category'):
        #    search['category'] = str(request.GET['category'])

        # Generate base queryset
        queryset = self.model.objects.all().select_related('city')

        #  Apply search term affect to refine queryset
        if 'tag' in search:
            tag = search['tag']
            #tag = self.model.clean_tag(search['tag'])
            queryset = queryset.filter(tags__name=tag)

        if 'country' in search:
            queryset = queryset.filter(country=search['country'])

        if 'region' in search:
            queryset = queryset.filter(region=search['region'])

        if 'city' in search:
            queryset = queryset.filter(city=search['city'])

        if 'search_terms' in search:
            # Really simple, ultra slow search system, until we set up
            # elastic / woosh / whatever
            terms = search['search_terms']
            for term in terms:
                t = term.strip()
                queryset = queryset & (
                        queryset.filter(title__icontains=term)
                        | queryset.filter(summary__icontains=term)
                    )

        #if 'category' in search:
        #    search['category'] = _category(search['category'].split())
        #    results = results.filter(category=search['category'].split())

        #########################################
        # Now, add tab, defaulting to the default specified by None
        tab_name = self.kwargs.get('tab') or self.browse_tabs[None]
        tab_filter = self.browse_tabs[tab_name]
        if tab_filter:
            queryset = tab_filter(queryset)

        #########################################
        # Now add pagination to results
        results = queryset
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)
        objects = list(page.object_list)
        #########################################

        nouns = "%ss" % self.noun
        c = {
                'queryset': queryset,
                'list': objects,
                'search': search,
                'tab': IsActive(tab_name),
                'is_search': any(search.values()),
                'page': page,
                #'tags': tags,
                'target_view_name': self.get_url_name(),
                nouns: objects,
                'model_class': self.model_class,
                #'tab': IsActive(ordering)
            }

        return c


##########################################
# Management interface

class FormBaseMixin(object):
    never_creates = False
    def get_object_for_form(self, request):
        return self.get_object(request)

    def post(self, request, *a, **k):
        """
        Handle form submission creating a new InfoBase object, or editing an
        existing one
        """
        instance = self.get_object(request)
        form = self.get_form(request, instance=instance)
        extra_form = None
        valid = form.is_valid()
        if self.extra_form:
            extra_form = self.get_extra_form(request, instance=instance)
            valid = extra_form.is_valid() and valid

        if not valid:
            # Return standard look.
            return self.get(request)

        redirect_result = self.redirect_parent_view()
        # Redirect to parent view by default

        if self.never_creates:
            form.save()
            if extra_form:
                extra_form.save()
            return redirect_result

        obj = form.save(commit=False)

        if extra_form:
            extra_form.save()

        if not obj.id:
            # Probably is creating: need to set user id
            obj.user = request.user
            obj.save()

            # Do any extra stuff now that the obj for sure has an ID (e.g.
            # associate location with object)
            if hasattr(form, 'after_save_setup'):
                form.after_save_setup()

            redirect_result = self.after_creation(obj)
            if self.CREATION_MESSAGE:
                messages.success(request, self.CREATION_MESSAGE)

            if not redirect_result:
                # If nothing specified, just redirect to the newly created
                # object
                redirect_result = redirect(obj.get_absolute_url())
        obj.save()

        return redirect_result


    def get_form(self, request, instance=None):
        if request.method == 'POST':
            form = self.form(request.POST, instance=instance)
        else:
            form = self.form(instance=instance)
        form.helper.form_id = "%s_edit" % self.noun
        form.helper.form_action = ''
        return form

    def after_creation(self, request):
        pass

class CreateInfo(Info, LoginRequiredMixin, FormBaseMixin):
    template_interfix = "manage/"
    template_basename = "create"
    breadcrumb = _('Create')
    CREATION_MESSAGE = ''


    def get_object(self, request):
        """
        Returns None since nothing has been created yet.
        """
        return None

    def get_context_data(self, request):
        form = self.get_form(request)
        return {
                'form': form,
            }



class ManageInfo(ViewInfo, LoginRequiredMixin):
    template_interfix = "manage/"
    DELETION_MESSAGE = ''
    UPDATED_MESSAGE = ''

    def check_permission(self, request, ctx):
        if not ctx.get('can_edit'):
            raise PermissionDenied(_("You don't have permission to manage this."))

    @classmethod
    def get_url_name(cls):
        s = "%s_manage_%s" % (cls.noun, cls.template_basename)
        return s

#class ManageEditInfo(ManageInfo, FormBaseMixin):
class ManageEditInfo(FormBaseMixin, ManageInfo):
    template_basename = "edit"
    breadcrumb = _('Manage details')
    extra_form = None

    def get_more_context(self, request, obj):
        extra_form = None
        if self.extra_form:
            extra_form = self.get_extra_form(request, instance=obj)
        return {
            'form': self.get_form(request, instance=obj),
            'extra_form': extra_form,
        }


class ManageMembersInfo(ManageInfo):
    template_basename = "members"
    breadcrumb = _('Manage')

    def post(self, *a, **k):
        return self.get(*a, **k)

    def get_more_context(self, request, obj):
        # TODO needs heavy refactor with make_manage_user_forms_context
        # Depending on different fields, construct the stuff, ya' dig?
        c = {}
        if 'user_access' in self.member_field_names:
            info = self.member_access['user_access']
            kwargs = { self.noun: obj }
            c = make_manage_user_access_forms_context(
                            request, obj, kwargs, info['model'])

        elif 'members' in self.member_field_names:
            c = make_manage_user_forms_context(request, obj, obj.members)

        return c




class ManageUploadBaseInfo(ManageInfo):
    """
    Can be subclassed for either Gallery or Files.
    """
    PAGE_SIZE = 30

    def get_more_context(self, request, obj):
        # Add sortability (disabled for now)
        #ordering = request.GET.get('ordering', '')
        #ordering = _one_of(ordering, "upload_date", "title")
        #ordering = _one_of(ordering, "upload_date", "title")

        # And pagination
        page_number = request.GET.get('page', request.GET.get('page', 1))

        # Paginate results
        queryset = self.get_queryset(obj)
        #results = queryset.order_by(ordering)
        results = queryset
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)
        files = page.object_list

        # Manually generate CSRF token for AJAX request
        csrf_token = get_token(request)

        return {
                'page': page,
                'photos': files,
                'files': files,
                'csrf_token': csrf_token,
            }

        return c


class ManageEditUploadBaseInfo(ManageInfo):
    """
    Superclass useful to create Media and File management views.

    Somewhat messy, since it was copied from a function based view, but it
    works.
    """

    def post(self, *a, **k):
        return self.get(*a, **k)

    def get(self, request, *a, **k):
        super_get = super(ManageEditUploadBaseInfo, self)

        # Generate relevant context data
        ctx = self.get_context_data(request)
        
        Form = self.form
        obj = ctx['obj']
        queryset = self.get_queryset(obj)

        # Do form actions
        action = request.GET.get('action')
        file_ids = request.GET.getlist('files')

        # Further refine queryset with filter based on IDs
        files = queryset.filter(id__in=file_ids)

        if action == 'delete':
            # Delete all that match query, and return
            files = self.exclude_undeletable(obj, files)
            number = files.count()
            if hasattr(files, "deleted"):
                files.update(deleted=True)
            else:
                # Perform hard delete
                files.delete()
                if self.DELETION_MESSAGE:
                    messages.success(request, self.DELETION_MESSAGE % number)

            # File delete, move on!
            return self.redirect_parent_view()

        # Otherwise, display file management view
        forms = []
        if request.method == 'POST':
            all_good = True
            for f in files:
                # Loop through and validate all forms
                form = Form(request.POST, instance=f, prefix=f.id)
                forms.append(form)
                if not form.is_valid():
                    all_good = False

            if all_good:
                # All good, save all forms then  redirect to main page
                for form in forms:
                    form.save()

                number = len(forms)
                if self.UPDATED_MESSAGE:
                    messages.success(request, self.UPDATED_MESSAGE % number)
                # Successful!
                return self.redirect_parent_view()

        else:
            for f in files:
                forms.append(Form(instance=f, prefix=f.id))

        self.add_breadcrumbs(request, ctx)

        ctx.update({
                'files': files,
                'forms': forms,
                'action': action,
            })

        return render(request, self.get_template_name(), ctx)


