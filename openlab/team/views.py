from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

# 1st party
from openlab.core.generic_views import *
from openlab.users.models import User
from openlab.gallery.views import ManageGalleryBase, ManageGalleryEditBase,\
                            ViewGalleryBase, ViewPhotoBase
from openlab.activity.views import ViewActivityStreamBase, ViewFollowersBase
from openlab.project.models import Project
from openlab.location.generic_views import CountryListBase

# local
from .models import Team
from .forms import CreateTeamForm, EditTeamForm

class Base:
    """
    Mix-in to establish everything about teams.

    When subclassing more core generic views, add this in to get all the magic.
    """
    model = Team
    noun = 'team'
    model_class = 'team'
    field = 'slug'
    template_prefix = 'team/'
    actions = ('follow_toggle',)
    extra_form = None
    member_field_names = ['members']

    browse_tabs = {
            "active": (lambda qs: qs.filter(team_projects__isnull=False)
                            | qs.filter(permissions__isnull=False)),
            "all": False,
            None: "active", # default
        }


class TeamList(ListInfo, Base):
    breadcrumb = _('People')


class TeamCountryList(CountryListBase, Base):
    breadcrumb = _('Teams by Country')
    parent_view = TeamList


class TeamCreate(CreateInfo, Base):
    parent_view = TeamList
    form = CreateTeamForm

    def after_creation(self, obj):
        # Add creator to team
        obj.members.add(obj.user)


class TeamView(ViewOverviewInfo, Base):
    parent_view = TeamList

    def get_more_context(self, request, obj):
        #projects = Project.objects.filter(team=self)
        projects = obj.team_projects.all()

        return {
                #'files_by_folder': files_by_folder,
                #'files': files,
                'projects': projects,
            }


class TeamViewActivity(ViewActivityInfo, Base):
    parent_view = TeamView


class TeamViewMembers(ViewMembersInfo, Base):
    parent_view = TeamView


class TeamViewFollowers(ViewFollowersBase, Base):
    parent_view = TeamView


class TeamViewGallery(ViewGalleryBase, Base):
    parent_view = TeamView


class TeamViewPhoto(ViewPhotoBase, Base):
    parent_view = TeamViewGallery


### Team management
class TeamManageMembers(ManageMembersInfo, Base):
    parent_view = TeamView # Manage members is top thing
    members = ['members']


class TeamManageGallery(ManageGalleryBase, Base):
    """
    Page where you can upload new gallery photos and delete etc existing ones
    """
    parent_view = TeamManageMembers
    edit_view_name = 'team_manage_gallery_edit'


class TeamManageEdit(ManageEditInfo, Base):
    """
    Editing details about the team :)
    """
    parent_view = TeamManageMembers
    form = EditTeamForm

