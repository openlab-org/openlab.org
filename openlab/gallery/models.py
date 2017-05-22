# python
import os.path

# django
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import formats
from django.utils.translation import ugettext as _

# 3rd-ish party
from s3uploader.models import GenericUploadableMixin

# first party
from openlab.prequeue.models import PreviewBaseClass
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


class Photo(PreviewBaseClass, CountedBase, GenericUploadableMixin):
    COUNTED_SCOPE = 'gallery'
    class Meta:
        unique_together = (CountedBase.unique_together('gallery'), )
        index_together = (CountedBase.unique_together('gallery'), )

    class PrequeueMeta:
        FILE_FIELD = 'path'

    class S3UploadableMeta:
        file_field = 'path'
        is_ready_field = 'is_uploaded'

        @staticmethod
        def get_object(request, filename, variables):
            gallery_id = variables.get('gallery_id')
            gallery = Gallery.objects.get(id=gallery_id)
            user = request.user
            return Photo(gallery=gallery, user=user)

        @staticmethod
        def on_upload_end(photo, request):
            photo.enqueue_preview_generation()

        @staticmethod
        def generate_filename(photo_model, original_filename):
            return photo_model.path_builder(original_filename)

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

    is_uploaded = models.BooleanField(default=False,
            help_text=_('Has the file successfully finished uploading?'))

    def __str__(self):
        # XXX
        # Important hack: this exact format is required for the
        # PhotoSelect2Widget in order to display photo previews.

        info = self.title
        if not self.preview_ready:
            return u"NotReady %s" % info
        else:
            return u"%s | %s" % (self.preview_image_thumb.url, info)


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

    @classmethod
    def copy_from(cls, prequeable):
        """
        Creates a photo based on the given prequeuable, used for copying over
        from file models and photo models to a new gallery for releases
        """
        kwds = dict(
            preview_image_thumb=prequeable.preview_image_thumb,
            preview_image=prequeable.preview_image,
            preview_file=prequeable.preview_file,
            preview_html=prequeable.preview_html,
            preview_tried=prequeable.preview_tried,
            preview_tried_date=prequeable.preview_tried_date
        )
        obj = cls(**kwds)

        cls.description = getattr(prequeable, 'description', None) or ''
        cls.title = getattr(prequeable, 'description', None) or ''
        cls.is_uploaded = True

        return obj




#class Media(PreviewBaseClass): # disabled
#    gallery = models.ForeignKey(Gallery,
#            help_text=_("Parent gallery"))
#
#    path = models.FileField(
#            upload_to=path_builder,
#            help_text=_("Actual file"))
#
#    title = models.CharField(max_length=255,
#            blank=True,
#            help_text=_("Title of this photo"))
#
#    description = models.TextField(max_length=2048,
#            blank=True,
#            help_text=_("A longer description, or notes about this photo"))
#
#    class PrequeueMeta:
#        FILE_FIELD = 'path'



class MediaLink(PreviewBaseClass):
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
    source = models.CharField(max_length=16,
                        choices=SOURCES)

    class PrequeueMeta:
        URL_FIELD = 'url' 

