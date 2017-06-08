# python
import os.path

# django
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import formats
from django.utils.translation import ugettext as _

# first party
from openlab.counted.models import ScopeBase, CountedBase

def file_path_builder(instance, filename):
    return instance.path_builder(filename)

def gallery_path_builder(gallery_id, filename):
    """
    Builds a path to a containing folder based on a project ID
    """
    s = "%06i" % gallery_id
    return os.path.join("gallery", s[:3], s[3:], filename)


class Gallery(ScopeBase):
    # By default, last photo uploaded, used for a thumbnail for the gallery
    photo = models.ForeignKey("Photo",
            null=True, blank=True,
            related_name="default_photo",
            help_text=_("Default photo"))


class Photo(CountedBase):
    COUNTED_SCOPE = 'gallery'
    class Meta:
        unique_together = (CountedBase.unique_together('gallery'), )
        index_together = (CountedBase.unique_together('gallery'), )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    gallery = models.ForeignKey(Gallery,
            related_name="photos",
            help_text=_("Parent gallery"))

    upload_date = models.DateTimeField('date uploaded',
                                auto_now_add=True)

    path = models.FileField(
            #upload_to=lambda i, filename: i.path_builder(filename),
            upload_to=file_path_builder,
            help_text=_("Path to raw photo"))

    title = models.CharField(max_length=255,
            blank=True,
            help_text=_("Title of this photo"))

    description = models.TextField(max_length=2048,
            blank=True,
            help_text=_("A longer description, or notes about this photo"))

    def __str__(self):
        return self.nice_title()

    def nice_title(self):
        # Ugh
        t = self.title.strip()
        if t:
            t += ' - '
        dt = formats.date_format(self.upload_date, "SHORT_DATETIME_FORMAT")
        return t + dt

    def get_absolute_url(self):
        # Ugh
        #project_path = self.gallery.project.all()
        return reverse('project.views.view_project_photo', args=[str(self.path)])

    def path_builder(self, filename):
        """
        Builds a path based on a file
        """
        # Go by gallery ID
        return gallery_path_builder(self.gallery_id, filename)


class MediaLink(models.Model):
    """
    MediaLink is useful for 3rd party hosted videos.
    """
    gallery = models.ForeignKey(Gallery,
            related_name="medialinks",
            help_text=_("Parent gallery"))

    url = models.URLField()

    title = models.CharField(max_length=255,
            blank=True,
            help_text=_("Title of this link"))

    description = models.TextField(max_length=2048,
            blank=True,
            help_text=_("A longer description, or notes about this link"))

    YOUTUBE = "youtube"
    VIMEO   = "vimeo"
    FLICKR  = "flickr"
    SOURCES = (
        (YOUTUBE, "YouTube"),
        (VIMEO,   "Vimeo"),
        (FLICKR,  "Flickr"),
    )
    source = models.CharField(max_length=16, choices=SOURCES)
