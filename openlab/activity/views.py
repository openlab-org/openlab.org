from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from openlab.users.models import User
from django.core.paginator import Paginator

from django.core.exceptions import PermissionDenied

#################################
# Activity stream stuff
from actstream import registry
from actstream.models import actor_stream, model_stream, action_object_stream, target_stream
from actstream.models import following, followers, Follow
from actstream.actions import follow, unfollow

from openlab.core.generic_views import ViewInfo#, RedirectException

def _stream_of_following(actor):
    stream = None

    # TODO move somewhere else
    registry.register(User)

    for following in Follow.objects.filter(user=actor):
        if not stream:
            stream = actor_stream(following.follow_object)
        else:
            stream = stream | actor_stream(following.follow_object)
    return stream

def _all_related(obj):

    # TODO move somewhere else
    registry.register(User)

    return actor_stream(obj) | action_object_stream(obj) | target_stream(obj)

def stream(actor, stream_type=None):
    """
    helper function
    """


    # TODO move somewhere else
    registry.register(User)

    if not stream_type:
        if isinstance(actor, type):
            stream_type = 'model_stream'
        else:
            stream_type = 'all'

    func = {
            'actor_stream': actor_stream,
            'model_stream': model_stream,
            'following': _stream_of_following,
            'all': _all_related,
        }[stream_type]
    return func(actor)


class ViewFollowersBase(ViewInfo):
    template_basename = "followers"
    breadcrumb = _('Followers')

    def get_more_context(self, request, obj):
        # Possibly will need to paginate if followers ever exceed 100 etc
        ctx = {}
        ctx['followers'] = followers(obj)
        return ctx

class ViewActivityStreamBase(ViewInfo):
    template_basename = "activity"
    breadcrumb = _('Activity')
    PAGE_SIZE = 100
    def get_more_context(self, request, obj):

        # And pagination
        page_number = request.GET.get('page', 1)

        # Paginate results
        results = stream(obj)
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)
        actions = page.object_list

        return {
                'page': page,
                'actions': actions,
            }

