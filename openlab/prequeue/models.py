import re
import os.path

from django.db import models
from openlab.users.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from s3uploader.models import GenericUploadableMixin

from . import tasks

def thumb_builder(instance, filename):
    return instance.preview_path_builder('thumb', filename)

def image_builder(instance, filename):
    return instance.preview_path_builder('image', filename)

def preview_builder(instance, filename):
    return instance.preview_path_builder('preview', filename)


def _is_svg(file_field):
    if not file_field:
        return False
    base, ext = os.path.splitext(file_field.name)
    return ext in (".svg",)

def _is_doc(file_field):
    if not file_field:
        return False
    base, ext = os.path.splitext(file_field.name)
    return ext in (".odt",".odp",".odg",".ods",".pdf")

class PreviewBaseClass(models.Model):
    """
    Base class representing a previewable model.
    """
    class Meta:
        abstract = True

    # Image path for a thumb preview
    preview_image_thumb = models.ImageField(blank=True,
            upload_to=thumb_builder,
            help_text=_("Image thumb"))

    # Image path for full image (if applicable)
    preview_image = models.ImageField(blank=True,
            upload_to=image_builder,
            help_text=_("Full size image preview"))

    preview_file = models.FileField(
            blank=True,
            upload_to=preview_builder,
            help_text=_("File in alternative format for preview"))

    preview_html = models.TextField(blank=True,
            help_text=_("Text for a plug-in based preview of the file"))

    preview_tried = models.BooleanField(
            default=False,
            db_index=True,
            help_text=_("Have we yet tried encoding a preview for "
                        "this file? (ie or is it still on the queue)"))

    preview_tried_date = models.DateField(
            null=True, blank=True,
            help_text=_("When did we last try encoding a preview for "
                        "this file? (Useful for if we start supporting "
                        "new preview formats.)"))

    #__original_path = None
    #
    #def __init__(self, *args, **kwargs):
    #    super(PreviewBaseClass, self).__init__(*args, **kwargs)
    #    self.__original_path = self._prequeue_path()
    #
    #def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #    if self._prequeue_path() != self.__original_path and not kwargs.get('skip_preview_generation'):
    #        # Changed the path, need to update the previews for this file
    #        self.enqueue_preview_generation()
    #
    #    super(self.__class__, self).save(force_insert, force_update, *args, **kwargs)
    #    self.__original_path = self._prequeue_path()

    def _prequeue_path(self):
        return getattr(self, self.__class__.PrequeueMeta.FILE_FIELD)

    def _prequeue_after_download(self, local_file_path):
        if hasattr(self.__class__.PrequeueMeta, 'setup_file_data'):
            self.__class__.PrequeueMeta.setup_file_data(self, local_file_path)

    def _prequeue_extension(self):
        path = self._prequeue_path()
        return os.path.splitext(path.name)[-1].strip('. ')

    def get_extension(self):
        # Just copied here since its used in a template, should change
        # everything to get_extension
        path = self._prequeue_path()
        return os.path.splitext(path.name)[-1].strip('. ')

    @property
    def preview_ready(self):
        if not self.preview_tried:
            return False

        # Full preview must be one of those three
        p = (self.preview_image or self.preview_file or self.preview_html)
        return self.preview_image_thumb and p

    def preview_path_builder(self, t, filename):
        new_filename = "%s.%s" % (t, filename)
        return self.path_builder(new_filename)

    def enqueue_preview_generation(self):
        """
        Enqueue an task to generate / regenerate the preview and thumbnails of
        this particular file.
        """
        tasks.create_preview.delay(self.__class__.__name__, self.id)
        #tasks.create_preview(self.__class__.__name__, self.id)

    def preview_copy_to(self, other_previewable):
        """
        Copies the info from this one to the other_previewable object, useful
        for snapshotting file info, etc.
        """
        other_previewable.preview_image_thumb = self.preview_image_thumb
        other_previewable.preview_image = self.preview_image
        other_previewable.preview_file = self.preview_file
        other_previewable.preview_html = self.preview_html
        other_previewable.preview_tried = self.preview_tried
        other_previewable.preview_tried_date = self.preview_tried_date


    ###########################################
    # REFACTOR ALL BELOW
    @property
    def get_alt_format(self):
        if self.preview_file:
            base, ext = os.path.splitext(self.preview_file.name)
            return ext
        return None

    #####################################################################
    # v-- needs refactor --v
    # TODO reduce all of this cruft into JS client-side logic with a big-ol
    # "Play" button to enable

    @property
    def is_3d(self):
        return self.path.name.endswith('.stl') or (self.preview_file and
                self.preview_file.name.endswith('.stl'))

    @property
    def url_for_3d_preview(self):
        if self.path.name.endswith('.stl'):
            return self.path.url
        elif (self.preview_file and
                self.preview_file.name.endswith('.stl')):
            return self.preview_file.url
        return None

    @property
    def url_for_doc(self):
        if _is_doc(self.path):
            return self.path.url
        elif _is_doc(self.preview_file):
            return self.preview_file.url
        return None

    @property
    def url_for_svg(self):
        if _is_svg(self.path):
            return self.path.url
        elif _is_svg(self.preview_file):
            return self.preview_file.url
        return None
    #####################################################################

