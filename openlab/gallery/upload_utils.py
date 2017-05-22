import os
import shutil

from core.util import makedirs_to_path, recursive_permissions_on_path
from django.conf import settings


def save_photo(temp_file_name, filename, photo, gallery):
    # Determine directory
    # NOTE: this is all temporary unscalable stuff
    new_path = photo.path_builder(filename)
    full_new_path = os.path.join(settings.MEDIA_ROOT, new_path)

    # Make sure the directory exists
    makedirs_to_path(full_new_path)

    # Move to new location
    shutil.move(temp_file_name, full_new_path)

    # Set permission on everything 
    # NOTE: As with the rest of this area, this func is super
    # inefficient, and will not be useful for when we uloadt to S3
    recursive_permissions_on_path(settings.MEDIA_ROOT)

    # Assign path to the new location
    # photo.path = File(new_path)
    # Crazy hack from (https://code.djangoproject.com/ticket/15590) only
    # useful until we move to S3 directly
    photo.path = photo.path.field.attr_class(photo, photo.path.field, new_path)

    photo.save()
    gallery.photo = photo
    gallery.save()

    # Enqueue the preview generation into the work machine
    photo.enqueue_preview_generation()

