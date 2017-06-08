# django
from django.db import models
from openlab.users.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.conf import settings

# 1st party
from openlab.core.models import InfoBaseModel
from openlab.team.models import Team
from openlab.anthrome import anthrome_types

# local
from .fields import LicenseField


class ProjectPermission(models.Model):
    project    = models.ForeignKey("Project", related_name='%(class)s_permission')
    view       = models.BooleanField(default=True)
    contribute = models.BooleanField(default=True)
    change     = models.BooleanField(default=True)
    revert     = models.BooleanField(default=True)
    invite     = models.BooleanField(default=True)

    class Meta:
        abstract = True


class TeamPermission(ProjectPermission):
    team = models.ForeignKey(Team, related_name='project_%(class)s')


class UserPermission(ProjectPermission):
    user = models.ForeignKey(User, related_name='project_%(class)s')


class Project(InfoBaseModel):
    # TODO hardcoded path, should be put somewhere else
    PLACEHOLDER_IMAGE_URL = settings.STATIC_URL + 'core/images/placeholder_project.png'

    # The creator
    user = models.ForeignKey(User,
            related_name="project",
            help_text=_("Creator of the project"))

    # Or team
    team = models.ForeignKey(Team,
            related_name="team_projects",
            null=True, blank=True,
            help_text=_("Team that can manage the project"))

    # The latest stable release, blank if it has not yet been released
    release = models.ForeignKey("release.Release",
            related_name="latest_stable",
            null=True, blank=True,
            help_text=_("Latest stable release"))

    # The latest stable release, blank if it has not yet been released
    git_url = models.URLField(
            null=True, blank=True,
            help_text=_("URL to Git repository"))

    license = LicenseField(
            default="pd",
            help_text=_("License for the entire project"))

    user_access = models.ManyToManyField(User,
                related_name='permissions',
                through=UserPermission)

    team_access = models.ManyToManyField(Team,
                related_name='permissions',
                through=TeamPermission)

    forked_from = models.ForeignKey('Project',
            related_name='forks',
            null=True, blank=True,
            help_text=_("Project that this project was forked from"))

    dependencies = models.ManyToManyField('Project',
            related_name='used_by_projects',
            help_text=_("Sub-projects that this project uses"))

    biome = models.CharField(max_length=2,
            choices=anthrome_types.CHOICES,
            help_text=_("Choose the anthrome to which this project is most related to."))

    def fork(self, user, team=None):
        """
        Forks this project into a new one, copying all file instances.
        Pass "team" into this function to "fork as team"
        Returns the new instance, already saved.
        """
        p = Project(
                    license=self.license,
                    title=self.title,
                    biome=self.biome,
                    summary=self.summary,
                    slug=self.slug,

                    # Copy photo (but of course user cannot change it)
                    photo=self.photo,

                    user=user,
                    forked_from=self,
                )

        # Give the team ownership if specified
        if team:
            p.team = team
            p.copy_location_from(team)
        else:
            p.copy_location_from(user.profile)

        p.save()
        return p

    def get_absolute_url(self):
        return reverse('project', args=[str(self.hubpath)])

    def get_absolute_thread_url(self, thread):
        return reverse('project_thread', args=[str(self.hubpath), thread.id])

    def editable_by_user_id_list(self):
        # A lot of look ups here, later we should cache all user IDs using the
        # Project id as a lookup and then check cache
        user_ids = [self.user_id]
        if self.team:
            user_ids.extend([u.id for u in self.team.members.all()])
            user_ids.append(self.team.user_id)

        user_access = self.user_access.all()
        if user_access:
            user_ids.extend(u.id for u in user_access)

        team_access = self.team_access.all()
        if team_access:
            # Access all members of team
            for t in team_access:
                user_ids.extend(u.id for u in t.members.all())

        #cache.set("editable-by-userid-list-"+self.id, user_ids)
        return user_ids

    def editable_by(self, user=None, user_id=None):
        """
        Given either the user_id or the user object, check if this project is
        editable by that person.
        """
        user_id = user_id or user.id
        return user_id in self.editable_by_user_id_list()

    def is_featurable(self):
        """
        Does this project meet the requirements to be featured?
        """
        return self.release
