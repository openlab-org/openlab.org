"""
File where we keep all sorts of different "activity" event generators
"""

from datetime import datetime

from django.db.models.signals import post_init, post_save, m2m_changed
from django.utils.translation import ugettext as _
from openlab.users.models import User

from actstream import action, registry
import actstream.models

from openlab.project.models import Project, Revision
from openlab.team.models import Team
from openlab.discussion.models import Thread, Message


def project_save(sender, **kwds):
    project = kwds['instance']
    created = kwds['created']

    #creator = project.team or project.user
    creator = project.user

    # TODO move somewhere else
    registry.register(Project)

    if created:
        if project.forked_from:
            action.send(creator, action_object=project,
                        verb='forked',
                        target=project.forked_from)
        else:
            action.send(creator, target=project, verb='created')
    else:
        # Disabling "updated" event since it triggers too often (e.g. produces
        # double events for committing new revisions
        #action.send(creator, target=project, verb='updated')
        pass

post_save.connect(project_save, sender=Project)

def team_save(sender, **kwds):
    team = kwds['instance']
    created = kwds['created']

    # TODO move somewhere else
    registry.register(Team)

    if created:
        action.send(team.user, target=team, verb='created')
    else:
        action.send(team.user, target=team, verb='updated')

post_save.connect(team_save, sender=Team)


def message_save(sender, **kwds):
    message = kwds['instance']
    created = kwds['created']

    if created:
        action.send(message.user, target=message, verb='posted')

#post_save.connect(message_save, sender=Message)


