from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from openlab.users.models import User
from datetime import datetime
from django.conf import settings

from core.util import *

from ... import tasks


def do_any(model_class, model_id_lolunused, force=False):
    if model_class == 'FileModel':
        from project.models import FileModel
        objs = FileModel.objects.order_by('-id').all()
    elif model_class == 'Photo':
        from gallery.models import Photo
        objs = Photo.objects.order_by('-id').all()
    else:
        raise NotImplemented("Class %s not available" % model_class)


    for obj in objs:
        # And figure out the function
        if not obj.preview_tried or force:
            print("----------------------- NOW I'M DOING ", obj.id, "-------")
            tasks.populate_preview_model(obj)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            model = str(args[0])
            if args[1].strip() == 'ALL':
                model_id = any
            else:
                model_id = int(args[1])
        except:
            error("""Bad arguments. Call with two arguments: 'Photo 132' or
                'FileModel 123141', or "Photo ALL" to do all in reverse ID order.
                Optionally have 3rd arg 'force' or 'sync' after this to make
                the operation forced (ie even if preview exists) or
                synchronous.  """.replace("  ", ''))

        if model_id == any:
            return do_any(model, model_id, force=(len(args) > 2 and args[2] == 'force'))

        if len(args) > 2 and args[2] == 'force':
            print("FORCING")
            tasks.create_preview(model, model_id, force=True)
        elif len(args) > 2 and args[2] == 'sync':
            print("lol jk already synchronous")
            tasks.create_preview(model, model_id, force=True)
        else:
            tasks.create_preview(model, model_id)



