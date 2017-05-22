from django.utils.translation import ugettext as _

from django.core.paginator import Paginator

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from actstream.models import actor_stream, model_stream
from actstream.actions import follow, unfollow
from actstream import action

# 1st party
from openlab.core.generic_views import *
from openlab.activity.views import ViewActivityStreamBase, ViewFollowersBase
from openlab.users.models import User

# local
from .models import Profile
from .forms import *


TEMPLATE_LOCATION = 'accounts/%s.html'
def tem(s):
    return TEMPLATE_LOCATION % s

def _bc(request):
    request.breadcrumbs(_("People"), reverse('team_list'))

def user_profile(request, username, tab=''):
    ctx = {
        'tab': tab,
    }

    if username == request.user.username:
        user = request.user
        ctx['is_you'] = True
    else:
        user = User.objects.get(username=username)
        ctx['is_you'] = False

    ctx['the_user'] = user
    ctx['the_profile'] = user.profile

    _bc(request)
    if not tab:
        request.breadcrumbs(ctx['the_profile'].desired_name, request.path)

        # Insert projects & teams involved with
        ctx['projects'] = user.project.all()
        ctx['projects_permissions'] = user.project_userpermission.all()
        ctx['teams'] = user.teams.all()

    else:
        # Add the profile (first tab) as a breadcrumb...
        url = reverse('user_profile', args=(user.username,))
        request.breadcrumbs(ctx['the_profile'].desired_name, url)

    if tab == 'activity':
        request.breadcrumbs(_("Activity"), request.path)

    if tab == 'followers':
        request.breadcrumbs(_("Followers"), request.path)

    if tab == 'following':
        request.breadcrumbs(_("Following"), request.path)

    return render(request, tem('profile'), ctx)


def edit_profile(request):

    profile = request.user.profile
    form = EditProfileForm(request.POST or None, instance=profile)

    # Add the profile (first tab) as a breadcrumb...
    _bc(request)
    url = reverse('user_profile', args=(request.user.username,))
    request.breadcrumbs(profile.desired_name, url)
    request.breadcrumbs(_("Edit Profile"), request.path)

    action = request.POST.get('action', None)

    if form.is_valid():
        if action.lower() == 'save':
            form = form.save()
            profile.save()
            return redirect(user_profile, request.user.username)
        elif action.lower() == 'cancel':
            return redirect(user_profile, request.user.username)

    return render(request, tem('profile_edit'), {
        'form': form,
        'profile': profile,
        'action': action,
    })


##############################
# Class based views that hook into the standard hierarchy go here

class Base(object):
    """
    Mix-in to establish everything about Users

    When subclassing more core generic views, add this in to get all the magic.
    """
    model = User
    noun = 'user'
    varname = 'the_user'
    model_class = 'user'
    field = 'username'
    template_prefix = 'accounts/'
    never_creates = True
    actions = ('follow_toggle',)

    # Check for if this obj can edit the user
    can_edit = lambda s, obj, user: obj == user

    def get_extra_form(self, request, instance=None):
        # Adds an optional "extra" form instance based on 
        profile = instance.profile
        if request.method == 'POST':
            form = self.extra_form(request.POST, instance=profile)
        else:
            form = self.extra_form(instance=profile)
        form.helper.form_id = "%s_edit" % self.noun
        form.helper.form_action = ''
        return form

    def get_core_context(self, request, obj):
        return {
                'profile': obj.profile,
            }


####################################
## User views
class UserViewProfile(Base, ViewOverviewInfo):
    template_basename = "profile"

    def get_more_context(self, request, user):
        ctx = {}
        # Insert projects & teams involved with
        ctx['projects'] = user.project.all()
        ctx['projects_permissions'] = user.project_userpermission.all()
        ctx['teams'] = user.teams.all()
        ctx['the_profile'] = user.profile
        return ctx


class UserViewActivity(Base, ViewActivityStreamBase):
    parent_view = UserViewProfile
    template_basename = "activity"

class UserViewFollowers(Base, ViewFollowersBase):
    parent_view = UserViewProfile
    template_basename = "followers"


####################################
## User editing views
class UserEdit(Base, ManageEditInfo):
    parent_view = UserViewProfile
    form = OnlyEditUserForm
    extra_form = OnlyEditProfileForm
    template_basename = "edit"

class UserEditNotifications(Base, ManageEditInfo):
    parent_view = UserEdit
    template_basename = "notifications"
    breadcrumb = _("Notification preferences")
    form = EditNotificationsUserForm
    extra_form = EditNotificationsForm

class UserEditEmail(Base, ManageEditInfo):
    parent_view = UserEdit
    template_basename = "email"
    form = EditEmailForm

class UserEditPassword(Base, ManageInfo):
    parent_view = UserEdit
    breadcrumb = _("Password preferences")
    template_basename = "password"

class UserEditDelete(Base, ManageInfo):
    parent_view = UserEdit
    breadcrumb = _("Purge account")
    template_basename = "delete"

