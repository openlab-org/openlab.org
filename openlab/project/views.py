
# django
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# third party
# AJAX insert Uploader views
#from ajaxuploader.views.base import AjaxFileUploader

# first party
# Other apps
from openlab.team.models import Team

# Base views
from openlab.core.generic_views import *

# viewing by country
from openlab.location.generic_views import CountryListBase

from openlab.gallery.views import ManageGalleryBase, ManageGalleryEditBase,\
                            ViewGalleryBase, ViewPhotoBase

from openlab.wiki.views import ManageWikiBase, EditWikiBase, ViewWikiBase,\
                            EditHistoryWikiBase

from openlab.activity.views import ViewActivityStreamBase, ViewFollowersBase

from openlab.discussion.views import ListDiscussionsBase, ViewThreadBase, DiscussableMixin

from openlab.release.views import ManageReleasesBase, ManageReleasesNewBase,\
                            ManageReleasesEditBase, make_release_context



# local
# Imports from this app
from .forms import CreateProjectForm, EditProjectForm,\
        EditFileForm, AddDependencyForm, RevisionForm, RenameFileForm
from .models import Project, FileModel, Revision, UserPermission




class Base(object):
    """
    Mix-in to establish everything about Projects.

    When subclassing more core generic views, add this in to get all the magic.
    """
    model = Project
    noun = 'project'
    model_class = 'project'
    field = 'hubpath'
    template_prefix = 'project/'
    actions = ('follow_toggle', 'forking',)
    member_field_names = ['user_access']
    member_access = {
            'user_access': {
                'model': UserPermission,
            },
        }

    browse_tabs = {
            "stable": lambda qs: qs.exclude(release=None),
            "unstable": False,
            None: "stable", # default
        }

    def get_forking_args(self, request):
        team_id = request.POST.get('team_id')
        team = None
        if team_id:
            team = get_object_or_404(Team, id=team_id)

        return [request.user, team]


class ProjectList(ListInfo, Base):
    breadcrumb = _('Projects')


class ProjectCountryList(CountryListBase, Base):
    breadcrumb = _('Projects by Country')
    parent_view = ProjectList


class ProjectCreate(CreateInfo, Base):
    CREATION_MESSAGE = _("Awesome! You've created a new project. Now upload "
                        "relevant files in the Update tab.")

    parent_view = ProjectList
    form = CreateProjectForm
    extra_form = None

    def after_creation(self, obj):
        """
        Misc set up for the project after it has been created
        """

        # Check if namespace is for team or for user
        ns = self.kwargs.get('project_namespace')
        if ns == obj.user.username:
            # Creating solo object for user
            return

        # Otherwise, we are creating a project owned by a team, so we look up
        # the team

        # TODO: add proper checking, right now if you get here via a bad link,
        # and the team does not exist, then that's a problem.
        team = Team.objects.get(slug=ns)

        # make sure user can create with this team
        if not team.editable_by(obj.user):
            raise PermissionDenied("Can't create projects with this team.")

        obj.team = team

####################################
## Project release views

# For now, we use flat, normal views for this. This will make tweaking / cache
# optimizing easier in the future, since we can very granularly control the
# logic

def project_release(request, hubpath, template="project/release/release.html"):
    project = get_object_or_404(Project, hubpath=hubpath)
    if not project.release:
        # Project has not yet been released, just redirect to file view
        return redirect("project_files", hubpath)

    # Okay, there is a release, lets format this
    ctx = make_release_context(request, project)

    if request.GET.get('preview_refresh'):
        ctx['template_override'] = 'project/release/base_empty.html'

    return render(request, template, ctx)


####################################
## Project views

#class ProjectViewFiles(ViewOverviewInfo, Base):
class ProjectViewFiles(ViewInfo, Base):
    parent_view = ProjectList
    template_basename = 'files'

    @classmethod
    def breadcrumb(cls, ctx):
        return str(ctx.get('obj'))

    def get_more_context(self, request, obj):
        files_by_folder = obj.get_files_by_folder()

        return {
                'files_by_folder': files_by_folder,
                #'files': files,
                'subprojects': obj.dependencies.all(),
            }


class ProjectViewFile(ViewInfo, DiscussableMixin, Base):
    parent_view = ProjectViewFiles
    template_basename = 'file'
    #breadcrumb = _('File')

    @classmethod
    def breadcrumb(cls, ctx):
        f = ctx.get('file')
        return str(f)

    def get_more_context(self, request, obj):
        file_id = self.kwargs.get('file_id')
        f = get_object_or_404(FileModel, project=obj, deleted=False, id=file_id)
        c = { 'file': f }
        c.update(self.get_discussion_context(request, f, context_object=obj))
        return c


class ProjectViewOverview(ViewInfo, Base):
    parent_view = ProjectViewFiles
    template_basename = "about"
    breadcrumb = _('Overview')


class ProjectViewMembers(ViewMembersInfo, Base):
    parent_view = ProjectViewFiles


class ProjectViewForks(ViewActivityInfo, Base):
    template_basename = 'forks'
    parent_view = ProjectViewFiles

    def get_more_context(self, request, obj):
        # Maybe flatten tree?
        return {
                'forks': obj.forks.all(),
                'used_by_projects': obj.used_by_projects.all(),
            }


class ProjectViewGallery(ViewGalleryBase, Base):
    parent_view = ProjectViewFiles


class ProjectViewPhoto(ViewPhotoBase, Base):
    parent_view = ProjectViewGallery


################################
# Discussion stuff
class ProjectViewDiscussions(ListDiscussionsBase, Base):
    parent_view = ProjectViewFiles
    thread_view_name = "project_thread"

class ProjectViewThread(ViewThreadBase, Base):
    parent_view = ProjectViewDiscussions


################################
# Act stream stuff
class ProjectViewFollowers(ViewFollowersBase, Base):
    parent_view = ProjectViewFiles

class ProjectViewActivity(ViewActivityStreamBase, Base):
    parent_view = ProjectViewFiles

################################
# wiki info
class ProjectViewWiki(ViewWikiBase, Base):
    parent_view = ProjectViewFiles

class ProjectEditWiki(EditWikiBase, Base):
    parent_view = ProjectViewWiki

class ProjectEditHistoryWiki(EditHistoryWikiBase, Base):
    parent_view = ProjectViewWiki


###################################
# Project updating
#

class FakeQS(list):
    def all(self):
        return self


class ProjectUpdate(ViewInfo, Base):
    """
    Create a new project release
    """
    parent_view = ProjectViewFiles
    template_basename = 'update'
    template_interfix = 'update/'
    breadcrumb = _('Update')

    def get_more_context(self, request, obj):
        ###### 0. Get revision in progress, creating if does not exist
        revision = Revision.get_or_create_in_progress(obj, request.user)
        revision_form = RevisionForm(instance=revision)

        ###### 1. Get files for this particular revision
        files = list(revision.files.filter(deleted=False))
        #files_by_folder = FileModel.by_folder(files)
        no_changes = not files

        ###### 2. Get existing files for tip revision
        existing_files = list(obj.get_files())
        existing_files_by_folder = obj.get_files_by_folder(existing_files)

        ###### 3. Generate rename forms for both existing files and new files
        rename_file_forms = {}
        _all_files = files + existing_files

        fakeqs_files = FakeQS(existing_files)
        for f in _all_files:
            rename_file_forms[f.id] = RenameFileForm(instance=f,
                    tip_files=fakeqs_files)
        replacing_files = dict((f.replaces_id, f) for f in files if f.replaces_id)

        ###### 4. Tag existing (tip) files with "replaces_by" field, if it does
        #         have a counterpart in this revision
        for f in existing_files:
            if f.id in replacing_files:
                f.replaced_by = replacing_files[f.id]

        brand_new_files = filter(lambda f: not f.replaces, files)
        brand_new_files_by_folder = FileModel.by_folder(brand_new_files)

        #combined_files = existing_files + brand_new_files
        #combined_files_by_folder = FileModel.by_folder(combined_files)

        c = {
                'revision': revision,
                'no_changes':      no_changes,
                #'files': files,
                'rename_file_forms': rename_file_forms,
                #'folders': folders,
                #'files_by_folder': files_by_folder,
                'revision_form': revision_form,

                'existing_files': existing_files,
                'existing_files_by_folder': existing_files_by_folder,

                'brand_new_files': brand_new_files,
                'brand_new_files_by_folder': brand_new_files_by_folder,
                #'combined_files': combined_files,
                #'combined_files_by_folder': combined_files_by_folder,
            }
        return c


def _get_and_check_revision(request, revision_id):
    revision = get_object_or_404(Revision, id=revision_id)

    if request.user != revision.user:
        raise Exception("Illegal attempt to modify revision.")
    if revision.is_uploaded:
        raise Exception("Illegal attempt to modify finished revision.")
    return revision


@login_required
def project_update_delete_revision(request, revision_id):
    """
    Endpoint to delete given revision
    """
    revision = _get_and_check_revision(request, revision_id)
    revision.files.update(deleted=True)
    revision.delete()

    project_hubpath = revision.project.hubpath
    return redirect("project_files", project_hubpath)


def _check_is_tip(request, file_model):
    """Some routine permissions stuff, then returns if the file is tip."""
    revision = file_model.revision

    if not revision.is_uploaded:
        # Is modifying newly uploaded, do sanity checks
        if request.user != file_model.user:
            raise PermissionDenied("Illegal attempt to modify file.")
        if file_model.is_tip:
            raise PermissionDenied("Illegal attempt to modify tip file.")

        return False
    else:
        # Is trying to rename existing
        project = revision.project
        if not project.editable_by(request.user):
            raise PermissionDenied("Illegal attempt to modify project.")
        return True

@login_required
def project_update_rename_file(request):
    """
    Endpoint to delete given file (for update management)
    """
    if request.method != "POST":
        raise PermissionDenied("needs to be post")

    file_id = request.POST.get('file_id')

    file_model = get_object_or_404(FileModel, id=file_id)
    project = file_model.project
    #is_tip = _check_is_tip(request, file_model)

    tip_files = project.get_files()
    form = RenameFileForm(request.POST, instance=file_model,
                    tip_files=tip_files)
    if form.is_valid():
        form.save()

    project_hubpath = file_model.project.hubpath

    return redirect("project_update", project_hubpath)


@login_required
def project_update_delete_file(request, file_id):
    """
    Endpoint to delete given file (for update management)
    """
    file_model = get_object_or_404(FileModel, id=file_id)
    is_tip = _check_is_tip(request, file_model)
    project_hubpath = file_model.project.hubpath

    if is_tip:
        # Is modifying tip file, copy to a new file and add to revision
        d = dict(is_uploaded=False,
                 user=request.user,
                 project=file_model.project)
        revision = Revision.objects.get(**d)

        # Create replacement one
        file_model.change_into_replacement(revision)
        file_model.removed = True
        file_model.save()

    else:
        # Is modifying new file, means we "actually delete" (e.g. not mark as "removed")
        file_model.deleted = True
        file_model.save()

    return redirect("project_update", project_hubpath)


NOT_READY_YET_ERROR_MSG = ("Could not finish revision. "
            "Make sure to remove files which have failed to upload.")

@login_required
def project_update_revision_complete(request, revision_id):
    """
    Endpoint to "complete" a revision or mark it as completed.
    Will generate the necessary action, queue up thumb generation, and set all
    the necessary files to "tip"
    """
    # first off only allow post
    assert request.method == 'POST'

    revision = _get_and_check_revision(request, revision_id)
    revision_form = RevisionForm(request.POST, instance=revision)
    project_hubpath = revision.project.hubpath
    if revision_form.is_valid():
        # Valid successful revision
        revision_form.save(commit=False)
        try:
            revision.complete()
        except Revision.NotReadyYet:
            messages.error(request, NOT_READY_YET_ERROR_MSG)
            return redirect("project_update", project_hubpath)
    else:
        raise Exception("Invalid form submission!")

    return redirect("project_files", project_hubpath)


class ProjectViewRevision(ViewInfo, DiscussableMixin, Base):
    parent_view = ProjectViewActivity
    template_basename = 'revision'

    def breadcrumb(self, ctx):
        r = ctx.get('revision')
        return _("Revision %s") % r.number if r else _("Revision")

    def get_more_context(self, request, obj):
        revision_number = self.kwargs.get('revision_number')
        revision = get_object_or_404(Revision,
                project=obj,
                deleted=False,
                number=revision_number)
        revision.check_and_set_if_ready()
        files_by_folder = revision.get_files_by_folder()

        c = {
            'revision': revision,
            'files_by_folder': files_by_folder,
        }

        c.update(self.get_discussion_context(request,
                            revision, context_object=obj))
        return c




###################################
# Project management
#


# Manage files is top thing


class ProjectManageEdit(ManageEditInfo, Base):
    """
    Editing details about the Project :)
    """
    #parent_view = ProjectManageFiles
    parent_view = ProjectViewFiles
    form = EditProjectForm

class ProjectManageDependencies(ManageInfo, Base):
    template_basename = 'dependencies'
    breadcrumb = _("Dependencies")
    #parent_view = ProjectManageFiles
    parent_view = ProjectManageEdit

    def post(self, request, *a, **k):
        delete_id = request.POST.get('delete_id')
        project_add = request.POST.get('project_to_add')
        if delete_id:
            obj = self.get_object(request)
            dependency = get_object_or_404(Project, id=delete_id)
            obj.dependencies.remove(dependency)
        elif project_add:
            obj = self.get_object(request)
            dependency = get_object_or_404(Project, id=project_add)
            obj.dependencies.add(dependency)
        else:
            raise Exception("POST without anything real specified.")
        return self.get(request, *a, **k)

    def get_more_context(self, request, obj):
        c = super(ProjectManageDependencies, self).get_more_context(request, obj)
        add_dependency_form = AddDependencyForm()
        c.update({
                'dependencies': obj.dependencies.all(),
                'add_dependency_form': add_dependency_form,
            })
        return c

class ProjectManageWiki(ManageWikiBase, Base):
    #parent_view = ProjectManageFiles
    parent_view = ProjectManageEdit


class ProjectManageMembers(ManageMembersInfo, Base):
    #parent_view = ProjectManageFiles
    parent_view = ProjectManageEdit
    breadcrumb = _("Manage contributors")
    members = ['user_access', 'team_access']


class ProjectManageGallery(ManageGalleryBase, Base):
    """
    Page where you can upload new gallery photos and delete etc existing ones
    """
    parent_view = ProjectManageEdit
    edit_view_name = 'project_manage_gallery_edit'


class ProjectManageGalleryEdit(ManageGalleryEditBase, Base):
    """
    Page where you can add captions / edit all the different gallery photos
    you just selected.
    """
    # XXX for now unused
    parent_view = ProjectManageEdit
    breadcrumb = _("Edit photos")



class ProjectManageReleases(ManageReleasesBase, Base):
    """
    Page where you select the official release, create new releases, clone,
    delete, etc
    """
    parent_view = ProjectManageEdit


class ProjectManageReleasesNew(ManageReleasesNewBase, Base):
    """
    Page where you select the official release, create new releases, clone,
    delete, etc
    """
    parent_view = ProjectManageEdit


class ProjectManageReleasesEdit(ManageReleasesEditBase, Base):
    """
    Page where you select the official release, create new releases, clone,
    delete, etc
    """
    #parent_view = ProjectManageFiles
    parent_view = ProjectManageEdit











##############################
# No longer in use..:

class ProjectManageFiles(ManageUploadBaseInfo, Base):
    """
    Page where you can upload new files photos and delete etc existing ones
    """
    template_basename = 'files'
    breadcrumb = _("Update")
    parent_view = ProjectViewFiles
    def get_queryset(self, obj):
        return FileModel.objects.filter(project=obj, deleted=False)

    def get_more_context(self, request, obj):
        c = super(ProjectManageFiles, self).get_more_context(request, obj)
        c.update({
                'noun': _("file"),
                'list_template': "project/snippets/file_list.html",
                'upload_view_name': "project_ajax_upload",
                'edit_view_name': 'project_manage_files_edit',
            })
        return c

class ProjectManageFilesEdit(ManageEditUploadBaseInfo, Base):
    template_basename = 'files_edit'
    breadcrumb = _("Edit file details")
    form = EditFileForm
    parent_view = ProjectManageFiles

    def get_queryset(self, obj):
        return FileModel.objects.filter(project=obj, deleted=False)

    def exclude_undeletable(self, obj, files):
        # no need at the moment for filtering or "undeletable objects", I
        # believe
        return files
