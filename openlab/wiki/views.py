# django
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# third party
import reversion

# first party
from openlab.core.generic_views import ManageInfo, FormBaseMixin,\
                        ViewInfo, RedirectException
from openlab.discussion.views import DiscussableMixin

# local
from .models import WikiSite, WikiPage
from .forms import ManageWikiForm, EditPageForm, PageHistoryForm


class ViewPageBase(ViewInfo):
    def check_permission(self, request, ctx):
        site = ctx.get('wikisite')

        if not site:
            raise PermissionDenied(_("Site not yet created."))

        if site.is_disabled:
            raise PermissionDenied(_("Site disabled."))

        if not site.is_public and not ctx['obj'].editable_by(request.user):
            raise PermissionDenied(_("Site not enabled for public viewing."))


    def get_more_context(self, request, obj):
        obj = self.get_object(request)
        wikisite = obj.wikisite
        if not wikisite:
            return { 'wikisite': None }

        slug = self.kwargs.get('pageslug', 'index')
        ctx = {}
        try:
            wikipage = WikiPage.objects.get(slug=slug, site=wikisite)
        except WikiPage.DoesNotExist:
            wikipage = None

        can_edit = wikisite.public_editable or obj.editable_by(request.user)

        return {
                    'wikipage': wikipage,
                    'can_edit_wiki': can_edit,
                    'wikisite': wikisite,
                    'pageslug': slug,
                }

class ViewWikiBase(ViewPageBase):
    template_basename = "wiki"

    @classmethod
    def breadcrumb(cls, ctx):
        if 'wikipage' in ctx:
            return str(ctx['wikipage'])
        return _("Wiki")

def deslugify(slug):
    return slug.replace("-", " ").replace("_", " ").capitalize()

class EditWikiMixin(object):
    def post(self, request, *a, **k):
        return self.get(request)

    def check_permission(self, request, ctx):
        super(EditWikiBase, self).check_permission(request, ctx)
        site = ctx['wikisite']
        if site.is_disabled:
            raise PermissionDenied(_("Site disabled."))

        if not site.public_editable and not ctx['obj'].editable_by(request.user):
            raise PermissionDenied(_("Site not enabled for public editing."))

class EditWikiBase(ViewPageBase, EditWikiMixin):
    template_basename = "wiki_edit"

    def get_more_context(self, request, obj):
        ctx = super(EditWikiBase, self).get_more_context(request, obj)

        wikipage = ctx.get('wikipage')

        if not wikipage:
            isnt_index = ctx['pageslug'] != 'index'
            title = deslugify(ctx['pageslug']) if isnt_index else _("Welcome")
            initial = { 'title': title }
        else:
            initial = None

        if request.method == "POST":
            form = EditPageForm(request.POST, instance=wikipage)
            if form.is_valid():
                page = form.save(commit=False)
                if not page.slug or not page.site:
                    # first time saving, need to regenerate these things
                    page.site = ctx['wikisite']
                    page.slug = ctx['pageslug']

                # Generate markdown
                page.regenerate_markdown(obj)
                comments = form.cleaned_data['comments']

                # Old file model, create a revision
                with reversion.create_revision() as r:
                    page.save()
                    reversion.set_user(request.user)
                    reversion.set_comment(comments)

                # Now that its saved, no need to generate more ctx, instead
                # cut through callstack and respond with redirect
                raise RedirectException(self.redirect_parent_view())
                #return self.redirect_parent_view()
        else:
            form = EditPageForm(instance=wikipage, initial=initial)

        ctx['form'] = form
        return ctx


    @classmethod
    def breadcrumb(cls, ctx):
        if 'wikipage' in ctx:
            return _(u"%s (Edit)") % str(ctx['wikipage'])
        return _("Creating %s") % ctx.get('pageslug')


class EditHistoryWikiBase(ViewPageBase, DiscussableMixin, EditWikiMixin):
    template_basename = "wiki_edit_history"

    def get_more_context(self, request, obj):
        ctx = super(EditHistoryWikiBase, self).get_more_context(request, obj)

        wikipage = ctx.get('wikipage')

        if not wikipage:
            raise PermissionDenied(_("Page not yet created."))

        if request.method == "POST":
            form = PageHistoryForm(request.POST, instance=wikipage)
            if form.is_valid():
                version = form.get_version()
                version.revision.revert()
                # Now that its saved, no need to generate more ctx, instead
                # cut through callstack and respond with redirect
                raise RedirectException(self.redirect_parent_view())
                #return self.redirect_parent_view()
        else:
            form = PageHistoryForm(instance=wikipage)


        ctx['form'] = form

        ctx.update(self.get_discussion_context(request, wikipage, context_object=obj))
        return ctx

    @classmethod
    def breadcrumb(cls, ctx):
        return _(u"%s (History)") % str(ctx.get('wikipage'))


class ManageWikiBase(ManageInfo):#, FormBaseMixin):
    template_basename = 'wiki'
    breadcrumb = _("Manage wiki settings")

    def post(self, request, *a, **k):
        # Return standard look.
        return self.get(request)

    def get_more_context(self, request, obj):
        obj = self.get_object(request)

        if request.POST.get('action', False) == "create":
            wikisite = WikiSite()
            wikisite.save()
            obj.wikisite = wikisite
            obj.save()

        wikisite = obj.wikisite
        if not wikisite:
            return { 'wikisite': None }

        if request.method == "POST":
            form = ManageWikiForm(request.POST, instance=wikisite)
            if form.is_valid():
                form.save()

        form = ManageWikiForm(instance=wikisite)

        return {
                'form': form,
                'wikisite': wikisite,
            }




