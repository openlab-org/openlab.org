from django.utils.translation import ugettext as _

# 1st party
from openlab.notifications.models import new
from openlab.olmarkdown import util as olmarkdown_util

# local
from .models import Thread, Message

def message_save(sender, **kwds):
    message = kwds['instance']
    created = kwds['created']

    if not created:
        # only generate notificaitons for newly generated messages
        return

    # Loop through everyone subscribed
    subscribers = list(message.thread.subscribers.all())
    mentioned_usernames = olmarkdown_util.get_username_mentions(
                message.olmarkdown_rendered)

    mentioned_users = []
    if mentioned_usernames:
        mentioned_users = User.objects.filter(
                username__in=mentioned_usernames)

    name = message.user.profile.desired_name
    msg = _(u"%s replied in a discussion which "
            "you have participated in") % name
    url = message.get_absolute_url()

    for user in subscribers:
        if user.username in mentioned_usernames:
            continue # skip, we'll do those later
        if message.user == user:
            continue # skip, its me!
        new(user, msg, url=url, actor=message.user, topic=message)

    msg = _(u"%s mentioned you in a comment") % name
    for user in mentioned_users:
        if message.user == user:
            continue # skip, its me!
        new(user, msg, url=url, actor=message.user, topic=message)


def thread_save(sender, **kwds):
    thread = kwds['instance']
    created = kwds['created']

    if not created:
        # only generate notificaitons / actions for newly created threads
        return

def trigger_thread_save(thread):

    projects = list(thread.project_set.all())
    teams = list(thread.team_set.all())

    # NOTE: "anything"  should almost certainly be a list of length 1
    anything = list(projects + teams)
    if thread.user:
        name = thread.user.profile.desired_name
    else:
        name = "Someone"

    if anything:
        verb = _(u"started a discussion about %s") % str(anything[0])
    else:
        verb = _(u"created a new discussion")

    msg = u" ".join([name, verb])

    # Distill down to teams
    for project in projects:
        if project.team:
            teams.append(project.team)

    # Distill down to users
    users = []
    for team in teams:
        users.extend(list(team.members.all()))
    for project in projects:
        users.append(project.user)

    url = thread.get_absolute_url()
    # Notify project creator and/or team members
    for user in users:
        if thread.user == user:
            continue # skip, its me!
        new(user, msg, url=url, actor=thread.user, topic=thread)


