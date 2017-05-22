from django.db import models
from openlab.users.models import User
from django.utils.translation import ugettext as _

from openlab.project.models import Project


class FeaturedProject(models.Model):
    user = models.ForeignKey(User,
            related_name="featured_projects",
            help_text="User who last updated feature (ie admin)")

    # Time range for it being featured
    date_featured = models.DateTimeField(auto_now_add=True, editable=True)
    date_last_featured = models.DateTimeField(auto_now=True, editable=True)

    project = models.ForeignKey(Project,
                    help_text="Specify the project you want to feature!")

    # so we can have "this project was once featured"
    active = models.BooleanField(default=True, db_index=True)

    KEY = 'moderation:featuredprojects'

    def save(self, *a, **k):
        return super(FeaturedProject, self).save(*a, **k)

        # clear cache
        cache.set(cls.KEY, None)

    @classmethod
    def get_featured_projects(cls):
        # later replace with cached version
        featured_projects = cls.objects.filter(active=True).select_related('project')
        return [fp.project for fp in featured_projects]

        projs = cache.get(cls.KEY)
        if not projs:
            featured_projects = cls.objects.filter(active=True).select_related('project')
            projs = [fp.project for fp in featured_projects]
            cache.set(cls.KEY, projs, 30000)
        return projs
