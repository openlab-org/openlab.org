# django
from django.db import models
from openlab.users.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.conf import settings

# 3rd party
from taggit.managers import TaggableManager
import actstream

# 1st party
from openlab.core.models import InfoBaseModel


class Team(InfoBaseModel):
    # TODO hardcoded path, should be put somewhere else
    PLACEHOLDER_IMAGE_URL = settings.STATIC_URL + 'core/images/placeholder_team.png'

    # The creator
    user = models.ForeignKey(User,
            related_name="managed_team",
            help_text=_("Manager of the team"))

    # Members
    members = models.ManyToManyField(User,
            related_name="teams",
            help_text=_("Members in the team"))

    def get_absolute_url(self):
        """
        Initial team view
        """
        from . import views # TODO Fix this
        return reverse(views.TeamView.get_url_name(), args=[self.hubpath])

