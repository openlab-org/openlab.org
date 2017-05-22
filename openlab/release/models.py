# python
import os.path

# django
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields.json import JSONField

# first party
from openlab.project.fields import LicenseField, VersionNumberField

def file_path_builder(instance, filename):
    return instance.path_builder(filename)

def project_path_builder(project_id):
    """
    Builds a path to a containing folder based on a project ID
    """
    s = "%06i" % project_id
    return os.path.join(s[:3], s)


class Release(models.Model):
    """
    A single, immutable publishing of a project
    """

    class Meta:
        ordering = ["-creation_date"]

    # The project that this publishing represents
    project = models.ForeignKey("project.Project",
            related_name="releases",
            help_text=_("Project for this file"))

    # The revision "pegged" at this release
    revision = models.ForeignKey("project.Revision",
            related_name="releases",
            help_text=_("Revision for this file"))

    license = LicenseField(
            help_text=_("License for this release."))

    version = VersionNumberField(
            help_text=_("Version number for this release."))

    zip_path = models.FileField(
            null=True,
            blank=True,
            default=None,
            #upload_to=lambda i, f: i.path_builder(f),
            upload_to=file_path_builder,
            help_text="Location of zip file of all project files. "
                "Blank means it has not yet been prepared.")

    components = JSONField()

    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)

    summary = models.CharField(
            max_length=140,
            verbose_name=_("Summary"),
            help_text=_("Describe in in 140 characters or less. (No paragraphs.)"))

    text = models.TextField(
            verbose_name=_("Description"),
            help_text=_("Project description"))

    notes = models.TextField(
            verbose_name=_("Release notes"),
            help_text=_("Information about this, what's fixed, etc."))

    size = models.PositiveIntegerField(
            help_text=_("Size in bytes of the download"))

    gallery = False and models.ForeignKey(Gallery,
            null=True, blank=True,
            help_text=_("Combined photos and file previews for the release"))

    @property
    def gallery(self):
        return self.project.gallery

    def path_builder(self, filename):
        """ Builds a path for the zip file based on the project """
        base = "release"
        project_path = project_path_builder(self.project_id)

        # Put files in directories based on their individual version numbers
        return os.path.join(base, project_path, filename)

    @property
    def is_latest_release(self):
        return self.project.release == self

    def __str__(self):
        return u"%s v%s" % (self.project.title, self.version) 




