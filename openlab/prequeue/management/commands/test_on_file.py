from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError

from core.util import makedirs_to_path, recursive_permissions_on_path

import sys
import shutil
import os.path
from openlab.users.models import User
from datetime import datetime
from django.conf import settings

from core.util import *

from ... import tasks


def upload_complete(self, request, filename, *args, **kwargs):
    # remember the file name
    temp_file_name = self._dest.name

    # Close
    self._dest.close()

    # Get file size
    size = os.path.getsize(temp_file_name)

    # Get the project
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return fail(errors.NOTFOUND)

    if not project.editable_by(request.user):
        return fail(errors.PERMISSION)

    # First check if we are creating a new reversion of this file
    try:
        fm = FileModel.objects.get(
                project=project,
                original_filename=filename,
            )
    except FileModel.DoesNotExist:
        title = FileModel.make_title_from_filename(filename)

        # Create a new FileModel
        fm = FileModel(
                project=project,
                title=title,
                original_filename=filename,
                size=size,
                user=request.user,
            )
        is_new = True
    else:
        is_new = False



    # Determine directory
    # NOTE: this is all temporary unscalable stuff
    new_path = fm.path_builder(filename)
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
    # fm.path = File(new_path)
    # Crazy hack from (https://code.djangoproject.com/ticket/15590) only
    # useful until we move to S3 directly
    fm.path = fm.path.field.attr_class(fm, fm.path.field, new_path)

    if not is_new:
        # Old file model, create a revision
        with reversion.create_revision():
            fm.save()
            reversion.set_user(request.user)
            # Later add the option of comment text ----v
            #reversion.set_comment(request.GET.get("comment_text", ""))
    else:
        # Save the FileModel! :D
        fm.save()

    fm.path = fm.path.field.attr_class(fm, fm.path.field, new_path)

    # Enqueue the preview generation into the work machine
    fm.enqueue_preview_generation()

    return {"filemodel_info": fm.id}

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            path = str(args[0])
        except:
            error("""Bad arguments. Call with one argument which is a path.""")

        if path == 'LIST':
            print("--------- ALL SUPPORTED FORMATS")
            print("\n".join(list(tasks.handlers.CONVERTERS.keys())))
            error(":)")

        if not os.path.exists(path):
            error("%s does not exist" % path)


        from project.models import FileModel
        fn = os.path.basename(path)
        fm = FileModel(
                    user_id=1,
                    project_id=6661337
                )

        tmp_path = os.path.join(settings.MEDIA_ROOT, "xxxx", "test_on_file", fn)
        makedirs_to_path(tmp_path) # Make sure the directory exists

        shutil.copy(path, tmp_path)
        file_path = os.path.relpath(tmp_path, settings.MEDIA_ROOT)
        fm.path = fm.path.field.attr_class(fm, fm.path.field, file_path)
        tasks.populate_preview_model(fm)

        print("RESULT:")
        if fm.preview_image:
            print("---------- Preview Image, Thumb --------")
            print(fm.preview_image.path)
            print(fm.preview_image_thumb.path)
        else:
            print("!!! No preview image!")
        if fm.preview_html:
            print("---------- Preview HTML --------")
            print(fm.preview_html.path)
        if fm.preview_file:
            print("---------- Preview file --------")
            print(fm.preview_file.path)
        else:
            print("No preview file!")



